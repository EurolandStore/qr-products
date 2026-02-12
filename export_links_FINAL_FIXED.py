from pathlib import Path
from openpyxl import Workbook
import os

# ================= НАСТРОЙКИ =================
PRODUCTS_DIR = Path("products")

BASE_URL = "https://eurolandstore.github.io/qr-products/products/"
OUTPUT_FILE = "FINAL_QR_PRODUCT_LINKS.xlsx"
# ============================================

print("RUNNING FILE: export_links_FINAL_FIXED.py")
print("BASE_URL USED:", BASE_URL)
print("OUTPUT FILE:", OUTPUT_FILE)

# --- если файл существует, удаляем ---
if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE)
    print("Old file removed")

wb = Workbook()
ws = wb.active
ws.title = "Products"

# --- ЯВНЫЕ МАРКЕРЫ ---
ws.append(["GENERATED_BY", "export_links_FINAL_FIXED.py"])
ws.append(["BASE_URL_USED", BASE_URL])
ws.append([])
ws.append(["SKU", "PRODUCT_URL"])

count = 0

for product_dir in sorted(PRODUCTS_DIR.iterdir()):
    if not product_dir.is_dir():
        continue

    sku = product_dir.name.strip()
    if not sku:
        continue

    url = BASE_URL + sku + "/index.html"

    # ПИШЕМ ЧИСТЫЙ ТЕКСТ, НЕ ФОРМУЛУ
    ws.append([sku, url])
    count += 1

wb.save(OUTPUT_FILE)

print("✅ Excel file created:", OUTPUT_FILE)
print("Products exported:", count)
