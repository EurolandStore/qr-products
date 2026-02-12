import pandas as pd
from pathlib import Path

BASE_DIR = Path(r"C:\Users\marsf\Documents\GitHub\qr-products")
EXCEL_FILE = BASE_DIR / "FINAL_QR_PRODUCT_LINKS.xlsx"
IMAGES_DIR = BASE_DIR / "assets"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

# =========================
# ПРОВЕРКИ
# =========================
if not EXCEL_FILE.exists():
    raise FileNotFoundError(f"❌ XLS файл не найден: {EXCEL_FILE}")

if not IMAGES_DIR.exists():
    raise FileNotFoundError(f"❌ Папка с изображениями не найдена: {IMAGES_DIR}")

# =========================
# ЧТЕНИЕ EXCEL
# =========================
df = pd.read_excel(EXCEL_FILE, header=3)
df.columns = df.columns.str.strip()

if "SKU" not in df.columns:
    raise ValueError(f"❌ Колонка SKU не найдена. Есть: {list(df.columns)}")

excel_skus = set(
    df["SKU"]
    .dropna()
    .astype(str)
    .str.strip()
)

# =========================
# ЧТЕНИЕ ИЗОБРАЖЕНИЙ
# =========================
image_skus = set(
    f.stem.strip()
    for f in IMAGES_DIR.iterdir()
    if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
)

# =========================
# СРАВНЕНИЕ
# =========================
missing_images = sorted(excel_skus - image_skus)

print("===================================")
print(f"SKU в Excel:          {len(excel_skus)}")
print(f"Изображений найдено:  {len(image_skus)}")
print(f"❌ БЕЗ ИЗОБРАЖЕНИЙ:   {len(missing_images)}")
print("===================================")

# =========================
# ОТЧЁТ
# =========================
if missing_images:
    out_file = BASE_DIR / "missing_images.xlsx"
    pd.DataFrame(
        {"SKU_without_image": missing_images}
    ).to_excel(out_file, index=False)
    print(f"📄 Отчёт сохранён: {out_file}")
else:
    print("🎉 Все SKU имеют изображения")
