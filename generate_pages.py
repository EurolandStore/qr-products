print("RUNNING:", __file__)
import csv
from pathlib import Path

BASE_DIR = Path(__file__).parent
PRODUCTS_DIR = BASE_DIR / "products"

LANGS = ["en", "ru", "uk", "de", "es", "it", "hr", "hu"]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<title>{name}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="../../assets/style.css">
</head>
<body>

<div class="lang">
  <a href="index.html">EN</a>
  <a href="ru.html">RU</a>
  <a href="uk.html">UA</a>
  <a href="de.html">DE</a>
  <a href="es.html">ES</a>
  <a href="it.html">IT</a>
  <a href="hr.html">HR</a>
  <a href="hu.html">HU</a>
</div>

<div class="header">
  <img src="../../assets/logo.png" alt="Euroland">
</div>

<div class="banner">
  <div class="product-image">
    <img src="product.jpg" alt="{name}" onerror="this.style.display='none'">
  </div>
</div>

<h1>{name}</h1>

<div class="box">
<b>Brand:</b> {brand}<br>
<b>Country:</b> {country}<br>
<b>Category:</b> {department}<br>
<b>Size:</b> {size}<br>
<b>SKU:</b> {sku}<br><br>

<b>Description:</b><br>
Authentic European product available at Euroland European Foods Market.
Selected for quality, traditional taste, and trusted origin.
</div>

</body>
</html>
"""

def main():
    csv_path = BASE_DIR / "products.csv"
    if not csv_path.exists():
        print("❌ products.csv not found")
        return

    rows_ok = 0

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            sku = row.get("SKU ID", "").strip()
            name = row.get("SKU Name", "").strip()

            if not sku or not name:
                continue

            product_dir = PRODUCTS_DIR / sku
            product_dir.mkdir(parents=True, exist_ok=True)

            for lang in LANGS:
                filename = "index.html" if lang == "en" else f"{lang}.html"
                html = HTML_TEMPLATE.format(
                    lang=lang,
                    sku=sku,
                    name=name,
                    brand=row.get("Brand", ""),
                    country=row.get("Country", ""),
                    department=row.get("Department", ""),
                    size=row.get("Size", "")
                )

                (product_dir / filename).write_text(html, encoding="utf-8")

            rows_ok += 1

    print(f"✅ Generated pages for {rows_ok} products")

if __name__ == "__main__":
    main()
