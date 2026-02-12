import json
from pathlib import Path



TEMPLATE = Path("template.html").read_text(encoding="utf-8")
CONTENT_DIR = Path("content")
PRODUCTS_DIR = Path("products")

LANG_MAP = {
    "en": "index.html",
    "ru": "ru.html",
    "ua": "ua.html",
    "de": "de.html",
    "es": "es.html",
    "it": "it.html",
    "hr": "hr.html",
    "hu": "hu.html"
}

PRODUCTS_DIR.mkdir(exist_ok=True)

for json_file in CONTENT_DIR.glob("*.json"):
    data = json.loads(json_file.read_text(encoding="utf-8"))

    sku = str(data.get("sku", "")).strip()
    if not sku:
        continue

    # ---------- PRODUCT NAME (НЕ ПЕРЕВОДИМ) ----------
    product_name = (
        data.get("name")
        or data.get("sku_name")
        or data.get("title")
        or ""
    )

    # ---------- GENERATE CONTENT ----------

    product_dir = PRODUCTS_DIR / sku
    product_dir.mkdir(parents=True, exist_ok=True)

    for lang, filename in LANG_MAP.items():
        i18n = data["i18n"].get(lang, {})
        sections = i18n.get("sections", {})
        meta = i18n.get("meta", {})

        # ---------- TAGS ----------
        tags_html = ""
        for tag in data.get("tags", []):
            tags_html += f'<span class="tag">{tag}</span>'

        # ---------- HISTORY ----------
        history_html = ""
        history_labels = i18n.get("history_labels", {})

        for h in i18n.get("history", []):
            key = h.get("key", "")
            label = history_labels.get(key, "")
            text = h.get("text", "")

            if not text:
                continue

            history_html += (
                '<div class="history-item">'
                + (f'<span class="year">{label}</span>' if label else "")
                + f'<p>{text}</p>'
                + '</div>'
            )

        # ---------- LABELS ----------
        brand_label = meta.get("brand", "")
        country_label = meta.get("country_of_origin", "")
        category_label = meta.get("category", "")
        size_label = meta.get("size", "")
        alcohol_label = meta.get("alcohol_content", "")

        # ---------- BUILD HTML ----------
        html = (
            TEMPLATE
            .replace("{{TITLE}}", product_name)
            .replace("{{TAGS}}", tags_html)
            .replace("{{BRAND_LABEL}}", brand_label)
            .replace("{{COUNTRY_LABEL}}", country_label)
            .replace("{{CATEGORY_LABEL}}", category_label)
            .replace("{{SIZE_LABEL}}", size_label)
            .replace("{{ALCOHOL_LABEL}}", alcohol_label)
            .replace("{{BRAND}}", data.get("brand", ""))
            .replace("{{COUNTRY}}", data.get("country_of_origin", ""))
            .replace("{{CATEGORY}}", data.get("category", ""))
            .replace("{{SIZE}}", data.get("size", ""))
            .replace("{{ALCOHOL}}", data.get("alcohol_content", ""))
            .replace("{{SKU}}", sku)
            .replace("{{DESC_TITLE}}", sections.get("description_title", ""))
            .replace("{{ING_TITLE}}", sections.get("ingredients_title", ""))
            .replace("{{PREC_TITLE}}", sections.get("precautions_title", ""))
            .replace("{{HISTORY_TITLE}}", sections.get("history_title", ""))
            .replace("{{DESCRIPTION}}", i18n.get("description", ""))
            .replace("{{INGREDIENTS}}", i18n.get("ingredients", ""))
            .replace("{{PRECAUTIONS}}", i18n.get("precautions", ""))
            .replace("{{HISTORY_ITEMS}}", history_html)
        )

        (product_dir / filename).write_text(html, encoding="utf-8")

print("✅ Pages generated")
