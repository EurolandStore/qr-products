# -*- coding: utf-8 -*-
"""
enrich_products.py
Mass-enrich 9k+ SKUs with EN descriptions/ingredients/precautions/history based on open web sources.

Inputs:
  - Products_MASTER.xlsx (columns: Department, Country, Brand, SKU ID, SKU Name, Size, Tags)

Outputs:
  - products_enriched.json  (dict keyed by sku_id)
  - products_enriched.ndjson (one json per line; handy for streaming)
  - cache/ (search + html extraction cache)

How it works:
  1) Build search queries per SKU (brand + sku name + keywords)
  2) DuckDuckGo search (no API key) -> top URLs
  3) Fetch + extract readable text (trafilatura)
  4) Heuristic fact extraction: ingredients/allergens/abv/notes
  5) Generate EN blocks in a consistent "premium grocery" style
  6) Always store sources; fallback safely when facts missing

IMPORTANT:
  - We do NOT copy-paste long text; we paraphrase + keep it short.
  - Ingredients are only filled when clearly found; otherwise: "see manufacturer labeling".
"""

import os
import re
import json
import time
import random
import hashlib
import argparse
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from rapidfuzz import fuzz

from duckduckgo_search import DDGS
import trafilatura

# ----------------------------
# CONFIG
# ----------------------------
DEFAULT_TIMEOUT = 25
MAX_URLS_PER_SKU = 5
MAX_FETCH_CHARS = 40_000  # limit extracted text stored/processed
WORKERS = 10              # thread pool size
SLEEP_BETWEEN_REQUESTS = (0.2, 0.8)  # polite jitter

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36"
)

SAFE_DEFAULT_INGREDIENTS = "Ingredients: see manufacturer’s labeling on the package."
SAFE_DEFAULT_HISTORY = "Produced under the {brand} name; refer to the manufacturer for brand and product background."
SAFE_DEFAULT_PRECAUTIONS = "Store as directed on the label. Keep in a cool, dry place unless otherwise noted."

ALCOHOL_PRECAUTIONS = (
    "Alcoholic beverage: intended for adults 21+. Do not drink during pregnancy. "
    "Enjoy responsibly; do not drink and drive."
)

# ----------------------------
# HELPERS
# ----------------------------
def ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)

def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", errors="ignore")).hexdigest()

def clean_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def title_case_brand(s: str) -> str:
    s = clean_spaces(s).lower()
    # Keep common brand formatting nice
    s = re.sub(r"\busa\b", "USA", s)
    return " ".join([w.capitalize() if not w.isupper() else w for w in s.split()])

def normalize_name(s: str) -> str:
    s = clean_spaces(s)
    # replace underscores etc.
    s = s.replace("_", " ")
    return s

def guess_category(dept: str, name: str) -> str:
    d = (dept or "").upper()
    n = (name or "").upper()
    # Fast rules
    if "WATER" in n or "WATER" in d:
        return "Water"
    if "BEER" in n or "BEER" in d:
        return "Beer"
    if "WINE" in n or "WINE" in d:
        return "Wine"
    if "VODKA" in n or "WHIS" in n or "RUM" in n or "TEQUILA" in n or "SPIRITS" in d:
        return "Spirits"
    if "JUICE" in n:
        return "Juice"
    if "SODA" in n or "SOFT DRINK" in n or "COLA" in n:
        return "Soft drink"
    if "CHEESE" in n or "DAIRY" in d:
        return "Dairy"
    if "CHOC" in n or "CANDY" in n or "CONFECTION" in d:
        return "Confectionery"
    if "PICKLED" in n or "OLIVE" in n:
        return "Pickled / Olives"
    if "SPICES" in d or "SPICE" in n or "SEASON" in n:
        return "Seasoning"
    return "Grocery"

def size_to_serving_hint(size: str) -> str:
    s = (size or "").strip()
    if not s:
        return ""
    return f" ({s})"

def is_alcohol(category: str, name: str) -> bool:
    c = (category or "").lower()
    n = (name or "").lower()
    if c in ("beer", "wine", "spirits"):
        return True
    if "abv" in n or "alc" in n:
        return True
    return False

# ----------------------------
# WEB SEARCH + FETCH (with cache)
# ----------------------------
@dataclass
class WebDoc:
    url: str
    title: str
    text: str

class WebCache:
    def __init__(self, base_dir: str = "cache"):
        self.base_dir = base_dir
        self.search_dir = os.path.join(base_dir, "search")
        self.page_dir = os.path.join(base_dir, "pages")
        ensure_dir(self.search_dir)
        ensure_dir(self.page_dir)

    def load_search(self, key: str) -> Optional[List[Dict]]:
        fp = os.path.join(self.search_dir, f"{sha1(key)}.json")
        if os.path.exists(fp):
            with open(fp, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def save_search(self, key: str, results: List[Dict]) -> None:
        fp = os.path.join(self.search_dir, f"{sha1(key)}.json")
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    def load_page(self, url: str) -> Optional[WebDoc]:
        fp = os.path.join(self.page_dir, f"{sha1(url)}.json")
        if os.path.exists(fp):
            with open(fp, "r", encoding="utf-8") as f:
                d = json.load(f)
            return WebDoc(**d)
        return None

    def save_page(self, doc: WebDoc) -> None:
        fp = os.path.join(self.page_dir, f"{sha1(doc.url)}.json")
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(asdict(doc), f, ensure_ascii=False, indent=2)

def ddg_search(query: str, max_results: int, cache: WebCache) -> List[Dict]:
    cached = cache.load_search(query)
    if cached is not None:
        return cached

    results: List[Dict] = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                # r: {'title','href','body'}
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                })
    except Exception as e:
        # Save empty to avoid repeated failures
        results = []
    cache.save_search(query, results)
    return results

def fetch_and_extract(url: str, cache: WebCache) -> Optional[WebDoc]:
    cached = cache.load_page(url)
    if cached is not None:
        return cached

    headers = {"User-Agent": USER_AGENT}
    try:
        time.sleep(random.uniform(*SLEEP_BETWEEN_REQUESTS))
        resp = requests.get(url, headers=headers, timeout=DEFAULT_TIMEOUT)
        if resp.status_code >= 400:
            return None
        html = resp.text
        # Use trafilatura for main text extraction
        downloaded = trafilatura.extract(html, include_comments=False, include_tables=False)
        text = clean_spaces(downloaded or "")
        if not text:
            # Fallback: BeautifulSoup text
            soup = BeautifulSoup(html, "html.parser")
            text = clean_spaces(soup.get_text(" "))
        title = ""
        try:
            soup = BeautifulSoup(html, "html.parser")
            title = clean_spaces(soup.title.get_text()) if soup.title else ""
        except Exception:
            title = ""

        text = text[:MAX_FETCH_CHARS]
        doc = WebDoc(url=url, title=title, text=text)
        cache.save_page(doc)
        return doc
    except Exception:
        return None

# ----------------------------
# FACT EXTRACTION (heuristics)
# ----------------------------
def extract_ingredients(text: str) -> Optional[str]:
    """
    Try to capture a clean "Ingredients: ..." line/paragraph.
    """
    if not text:
        return None
    t = text

    # Common markers
    patterns = [
        r"(Ingredients?\s*[:\-]\s*)(.{20,400})",
        r"(INGREDIENTS?\s*[:\-]\s*)(.{20,400})",
        r"(Состав\s*[:\-]\s*)(.{20,400})",  # sometimes on bilingual pages
    ]
    for pat in patterns:
        m = re.search(pat, t, flags=re.IGNORECASE)
        if m:
            blob = m.group(2)
            blob = re.split(r"(Nutrition|Allergen|Storage|Directions|Contains|May contain|Warning)\b", blob, flags=re.IGNORECASE)[0]
            blob = clean_spaces(blob)
            # keep reasonable chars
            blob = blob.strip(" .;")
            if len(blob) >= 15:
                return f"Ingredients: {blob}."
    return None

def extract_allergens(text: str) -> List[str]:
    if not text:
        return []
    allergens = []
    # common terms
    candidates = [
        ("gluten", r"\b(gluten)\b"),
        ("wheat", r"\b(wheat)\b"),
        ("barley", r"\b(barley)\b"),
        ("milk", r"\b(milk|dairy)\b"),
        ("soy", r"\b(soy|soya)\b"),
        ("egg", r"\b(egg)\b"),
        ("peanuts", r"\b(peanut)\b"),
        ("tree nuts", r"\b(almond|hazelnut|walnut|cashew|pistachio|pecan)\b"),
        ("sesame", r"\b(sesame)\b"),
        ("fish", r"\b(fish)\b"),
        ("shellfish", r"\b(shellfish|shrimp|crab|lobster)\b"),
    ]
    lower = text.lower()
    for name, pat in candidates:
        if re.search(pat, lower):
            allergens.append(name)
    # de-dup
    out = []
    for a in allergens:
        if a not in out:
            out.append(a)
    return out

def extract_abv(text: str) -> Optional[str]:
    if not text:
        return None
    # ABV patterns
    m = re.search(r"(\d{1,2}(?:\.\d{1,2})?)\s*%?\s*ABV", text, flags=re.IGNORECASE)
    if m:
        return f"{m.group(1)}% ABV"
    m = re.search(r"alc(?:ohol)?\s*[:\-]?\s*(\d{1,2}(?:\.\d{1,2})?)\s*%", text, flags=re.IGNORECASE)
    if m:
        return f"{m.group(1)}% ABV"
    return None

def pick_best_docs(docs: List[WebDoc], sku_name: str, brand: str) -> List[WebDoc]:
    """
    Rank docs by basic relevance (title/text contains brand/name tokens).
    """
    if not docs:
        return []
    bn = brand.lower()
    sn = sku_name.lower()
    ranked = []
    for d in docs:
        score = 0
        hay = (d.title + " " + d.text[:2000]).lower()
        if bn and bn in hay:
            score += 25
        # token overlap
        for tok in re.findall(r"[a-z0-9]+", sn)[:8]:
            if len(tok) >= 4 and tok in hay:
                score += 3
        # prefer shorter, cleaner pages (avoid junk)
        if 200 < len(d.text) < 12000:
            score += 5
        ranked.append((score, d))
    ranked.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in ranked[:3]]

# ----------------------------
# TEXT GENERATION (consistent style, no hallucinated ingredients)
# ----------------------------
def generate_description(category: str, sku_name: str, brand: str, size: str, tags: str, abv: Optional[str]) -> str:
    n = sku_name.upper()
    s_hint = size_to_serving_hint(size)

    # Phrase banks (light variety)
    openers = [
        "A well-balanced",
        "A classic",
        "A refreshing",
        "A flavorful",
        "A smooth",
        "A bright and satisfying",
    ]
    finishes = [
        "Great chilled or served as directed on the label.",
        "Perfect for everyday enjoyment.",
        "An easy pick for your pantry and your table.",
        "Ideal for sharing, pairing, or snacking.",
        "A convenient choice for quick meals and moments.",
    ]

    op = random.choice(openers)
    fin = random.choice(finishes)

    if category == "Water":
        sparkle = "sparkling" if ("SPARKLING" in n or "CARBONATED" in n) else "still"
        return f"{op} {sparkle} mineral water{ s_hint } with a clean, crisp finish. {fin}"
    if category == "Beer":
        extra = f" ({abv})" if abv else ""
        return f"{op} beer{extra}{ s_hint } with a lively character and a smooth finish. {fin}"
    if category == "Wine":
        extra = f" ({abv})" if abv else ""
        return f"{op} wine{extra}{ s_hint } crafted for easy sipping and food pairing. {fin}"
    if category == "Spirits":
        extra = f" ({abv})" if abv else ""
        return f"{op} spirit{extra}{ s_hint } with a clean profile and a warming finish. {fin}"
    if category == "Confectionery":
        return f"{op} sweet treat{ s_hint }—rich, comforting, and perfect with coffee or tea. {fin}"
    if category == "Dairy":
        return f"{op} dairy item{ s_hint } with a creamy texture and a clean, fresh taste. {fin}"
    if category == "Seasoning":
        return f"{op} kitchen staple{ s_hint } designed to mix, dissolve, and perform reliably in cooking and baking. {fin}"
    if category == "Pickled / Olives":
        return f"{op} brined bite{ s_hint } with a firm texture and bold, savory flavor. {fin}"

    # Grocery generic
    return f"{op} grocery item{ s_hint } made for convenient everyday use. {fin}"

def generate_precautions(category: str, allergens: List[str], alcohol: bool) -> str:
    parts = []
    if allergens:
        # make allergens readable
        parts.append("Allergen information: contains " + ", ".join(allergens) + ".")
    if alcohol:
        parts.append(ALCOHOL_PRECAUTIONS)
    # category storage hints
    if category in ("Dairy",):
        parts.append("Keep refrigerated; follow storage instructions on the label.")
    elif category in ("Confectionery", "Seasoning", "Grocery", "Pickled / Olives"):
        parts.append("Store in a cool, dry place. Refrigerate after opening if indicated.")
    elif category == "Water":
        parts.append("Store in a cool, dark place. Serve chilled.")
    else:
        parts.append(SAFE_DEFAULT_PRECAUTIONS)
    return " ".join(parts)

def generate_history(brand: str, sources: List[str], wiki_hint: Optional[str]) -> List[Dict]:
    # Keep it safe: only assert strong facts if we have a good hint (wiki or official)
    if wiki_hint:
        return [{"year": "—", "text": wiki_hint}]
    # default
    return [{"year": "—", "text": SAFE_DEFAULT_HISTORY.format(brand=brand)}]

def pick_wiki_hint(docs: List[WebDoc], brand: str) -> Optional[str]:
    """
    If wikipedia-like text appears, use a short, non-specific hint.
    We keep it conservative: no dates unless clearly present.
    """
    for d in docs:
        if "wikipedia" in d.url.lower():
            # ultra-short generic
            return f"{brand} is a recognized brand; see public references for background and brand history."
    return None

# ----------------------------
# SKU ENRICH
# ----------------------------
def build_queries(brand: str, sku_name: str, category: str) -> List[str]:
    b = clean_spaces(brand)
    n = clean_spaces(sku_name)
    base = f"{b} {n}"
    queries = [
        f'{base} ingredients',
        f'{base} allergen',
        f'{base} ABV' if category in ("Beer","Wine","Spirits") else f'{base} product',
        f'{b} official site',
        f'{b} history',
    ]
    # de-dup while preserving order
    out = []
    for q in queries:
        q = clean_spaces(q)
        if q and q not in out:
            out.append(q)
    return out

def enrich_one(row: Dict, cache: WebCache, max_urls: int = MAX_URLS_PER_SKU) -> Dict:
    sku_id = str(row.get("SKU ID", "")).strip()
    brand_raw = str(row.get("Brand", "")).strip()
    sku_name_raw = str(row.get("SKU Name", "")).strip()
    dept = str(row.get("Department", "")).strip()
    size = str(row.get("Size", "")).strip()
    tags = "" if pd.isna(row.get("Tags", "")) else str(row.get("Tags", "")).strip()

    brand = title_case_brand(brand_raw)
    sku_name = normalize_name(sku_name_raw)
    category = guess_category(dept, sku_name)
    alcohol = is_alcohol(category, sku_name)

    queries = build_queries(brand, sku_name, category)

    # Search -> URLs
    urls = []
    for q in queries[:3]:  # keep it fast
        results = ddg_search(q, max_results=6, cache=cache)
        for r in results:
            u = r.get("url", "")
            if not u or not u.startswith("http"):
                continue
            # light filtering
            if any(x in u.lower() for x in ["facebook.com", "instagram.com", "pinterest.com"]):
                continue
            if u not in urls:
                urls.append(u)
            if len(urls) >= max_urls:
                break
        if len(urls) >= max_urls:
            break

    # Fetch docs
    docs: List[WebDoc] = []
    for u in urls:
        d = fetch_and_extract(u, cache=cache)
        if d and d.text and len(d.text) > 120:
            docs.append(d)

    best_docs = pick_best_docs(docs, sku_name=sku_name, brand=brand)

    merged_text = " ".join([d.text for d in best_docs])
    merged_text = merged_text[:MAX_FETCH_CHARS]

    ingredients = extract_ingredients(merged_text)
    allergens = extract_allergens(merged_text)

    abv = extract_abv(merged_text) if alcohol else None

    description = generate_description(
        category=category,
        sku_name=sku_name,
        brand=brand,
        size=size,
        tags=tags,
        abv=abv
    )

    precautions = generate_precautions(category=category, allergens=allergens, alcohol=alcohol)

    # If ingredients missing but category strongly implies single-ingredient (water)
    if not ingredients:
        if category == "Water":
            ingredients = "Ingredients: natural water."
        else:
            ingredients = SAFE_DEFAULT_INGREDIENTS

    wiki_hint = pick_wiki_hint(best_docs, brand)
    history = generate_history(brand=brand, sources=[d.url for d in best_docs], wiki_hint=wiki_hint)

    sources = [{"name": (d.title or "Source").strip()[:120], "url": d.url} for d in best_docs]

    out = {
        "sku": sku_id,
        "brand": brand_raw,  # keep original if you want; change to brand for pretty
        "category": category,
        "size": size,
        "i18n": {
            "en": {
                "title": clean_spaces(sku_name.title()),
                "description": description,
                "ingredients": ingredients,
                "precautions": precautions,
                "history": history,
                "sources": sources
            }
        }
    }
    return out

# ----------------------------
# MAIN
# ----------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="Products_MASTER.xlsx", help="Path to Products_MASTER.xlsx")
    ap.add_argument("--out_json", default="products_enriched.json", help="Output JSON (dict keyed by sku)")
    ap.add_argument("--out_ndjson", default="products_enriched.ndjson", help="Output NDJSON (one per line)")
    ap.add_argument("--limit", type=int, default=0, help="Optional limit for testing; 0 = all")
    ap.add_argument("--max_urls", type=int, default=MAX_URLS_PER_SKU)
    args = ap.parse_args()

    df = pd.read_excel(args.input)
    if args.limit and args.limit > 0:
        df = df.head(args.limit)

    cache = WebCache("cache")

    enriched_by_sku: Dict[str, Dict] = {}

    # Sequential is safest for the web (less blocks). It will take time, but won't explode.
    # If you want faster later, we can add ThreadPoolExecutor with conservative rate limit per worker.
    with open(args.out_ndjson, "w", encoding="utf-8") as fnd:
        for _, r in tqdm(df.iterrows(), total=len(df), desc="Enriching"):
            row = r.to_dict()
            sku = str(row.get("SKU ID", "")).strip()
            item = enrich_one(row, cache=cache, max_urls=args.max_urls)
            enriched_by_sku[sku] = item
            fnd.write(json.dumps(item, ensure_ascii=False) + "\n")

    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(enriched_by_sku, f, ensure_ascii=False, indent=2)

    print(f"\nDone. Wrote:\n - {args.out_json}\n - {args.out_ndjson}\nCache folder: cache/")

if __name__ == "__main__":
    main()
