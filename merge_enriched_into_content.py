import json
import os

CONTENT_DIR = "content"
ENRICHED_FILE = "products_enriched.json"

FIELDS_TO_MERGE = [
    "description",
    "ingredients",
    "precautions",
    "history",
    "sources"
]

# ---------- load enriched ----------
with open(ENRICHED_FILE, encoding="utf-8") as f:
    enriched = json.load(f)

updated = 0
skipped = 0

for fname in os.listdir(CONTENT_DIR):
    if not fname.endswith(".json"):
        continue

    sku = fname.replace(".json", "")
    path = os.path.join(CONTENT_DIR, fname)

    if sku not in enriched:
        skipped += 1
        continue

    with open(path, encoding="utf-8") as f:
        product = json.load(f)

    en_old = product.setdefault("i18n", {}).setdefault("en", {})
    en_new = enriched[sku].get("i18n", {}).get("en", {})

    changed = False

    for field in FIELDS_TO_MERGE:
        if field in en_new and en_new[field]:
            if en_old.get(field) != en_new[field]:
                en_old[field] = en_new[field]
                changed = True

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(product, f, ensure_ascii=False, indent=2)
        updated += 1

print("MERGE completed")
print("Updated SKUs:", updated)
print("Skipped (not found in enriched):", skipped)
