import json
import re
import pandas as pd
from pathlib import Path

from content_generators import generate_en_content
from i18n_translator import generate_i18n_from_en


# ==============================
# CONFIG
# ==============================
EXCEL_FILE = "Products_MASTER.xlsx"
OUTPUT_DIR = Path("content")
TEMPLATE_FILE = Path("template_product.json")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==============================
# HELPERS
# ==============================
def safe_filename(value: str) -> str:
    """
    Make filename safe for Windows / GitHub / URLs
    """
    value = str(value).strip()

    # remove trailing .0 from excel numbers
    value = value.replace(".0", "")

    # replace forbidden characters
    value = re.sub(r'[\\/:*?"<>|]+', '-', value)

    # normalize spaces
    value = re.sub(r'\s+', ' ', value)

    return value


# ==============================
# LOAD DATA
# ==============================
template = json.loads(TEMPLATE_FILE.read_text(encoding="utf-8"))
df = pd.read_excel(EXCEL_FILE)

created = 0


# ==============================
# MAIN LOOP
# ==============================
for _, row in df.iterrows():
    sku_raw = str(row.get("SKU ID", "")).strip()
    if not sku_raw:
        continue

    # --- SAFE SKU (for filenames & paths) ---
    sku = safe_filename(sku_raw)

    # --- deep copy template ---
    product = json.loads(json.dumps(template))

    # --- BASIC FIELDS ---
    product["sku"] = sku
    product["name"] = str(row.get("SKU Name", "")).strip()
    product["brand"] = str(row.get("Brand", "")).strip()
    product["country_of_origin"] = str(row.get("Country", "")).strip()
    product["category"] = str(row.get("Department", "")).strip()
    product["size"] = str(row.get("Size", "")).strip()
    product["alcohol_content"] = ""
    product["image"] = f"../../assets/{sku}.jpg"

    tags = str(row.get("Tags", "")).strip()
    product["tags"] = [t.strip() for t in tags.split(",") if t.strip()]

    # ==============================
    # RESET I18N (EN = SOURCE OF TRUTH)
    # ==============================
    product["i18n"] = {"en": product["i18n"].get("en", {})}

    # ==============================
    # 1️⃣ GENERATE EN CONTENT
    # ==============================
    product["i18n"]["en"] = generate_en_content(
        product=product,
        en_block=product["i18n"]["en"]
    )

    # ==============================
    # 2️⃣ TRANSLATE EN → ALL LANGS
    # ==============================
    generate_i18n_from_en(product)

    # ==============================
    # 3️⃣ SAVE JSON
    # ==============================
    out_file = OUTPUT_DIR / f"{sku}.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)

    out_file.write_text(
        json.dumps(product, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    created += 1


print(f"✅ JSON created: {created}")
