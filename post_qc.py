import os
import json
import re
from urllib.parse import urlparse

CONTENT_DIR = "content"

# -------- helpers --------

def is_relevant_source(url: str, brand: str) -> bool:
    if not url:
        return False

    bad_domains = [
        "wikipedia.org",        # generic wiki noise
        "facebook.com",
        "instagram.com",
        "twitter.com",
        "pinterest.com",
        "opentermsarchive.org",
        "cbsox.com"             # пойманный мусор
    ]

    domain = urlparse(url).netloc.lower()

    if any(bad in domain for bad in bad_domains):
        return False

    brand_key = re.sub(r"[^a-z0-9]", "", brand.lower())
    domain_key = re.sub(r"[^a-z0-9]", "", domain)

    # если бренд хоть как-то читается в домене — ок
    if brand_key and brand_key[:6] in domain_key:
        return True

    # ритейлеры (разрешаем)
    retailers = [
        "amazon", "walmart", "publix", "metro",
        "winndixie", "totalwine", "instacart",
        "bakkal", "gastronom"
    ]
    if any(r in domain_key for r in retailers):
        return True

    return False


def fix_water_description(desc: str, title: str) -> str:
    """
    Fix sparkling / still mismatch using keywords and color codes.
    """
    t = (title or "").upper()

    # явные маркеры
    if any(k in t for k in ["NON-CARBONATED", "STILL", "BLUE"]):
        desc = re.sub(r"\bsparkling\b", "still", desc, flags=re.IGNORECASE)

    if any(k in t for k in ["SPARKLING", "CARBONATED", "GREEN"]):
        desc = re.sub(r"\bstill\b", "sparkling", desc, flags=re.IGNORECASE)

    return desc


# -------- main --------

fixed_sources = 0
fixed_water = 0
files = 0

for fname in os.listdir(CONTENT_DIR):
    if not fname.endswith(".json"):
        continue

    path = os.path.join(CONTENT_DIR, fname)

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    changed = False
    files += 1

    brand = data.get("brand", "")
    cat = data.get("category", "")

    en = data.get("i18n", {}).get("en", {})

    # ---- SOURCES CLEAN ----
    sources = en.get("sources", [])
    if sources:
        clean = []
        for s in sources:
            url = s.get("url", "")
            if is_relevant_source(url, brand):
                clean.append(s)

        if len(clean) != len(sources):
            fixed_sources += 1
            changed = True

        if not clean:
            clean = [{
                "name": "Public product information",
                "url": ""
            }]

        en["sources"] = clean

    # ---- WATER FIX ----
    if cat == "Water":
        desc = en.get("description", "")
        title = en.get("title", "")
        new_desc = fix_water_description(desc, title)

        if new_desc != desc:
            en["description"] = new_desc
            fixed_water += 1
            changed = True

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

print("Post-QC done")
print("Files processed:", files)
print("Sources cleaned:", fixed_sources)
print("Water descriptions fixed:", fixed_water)
