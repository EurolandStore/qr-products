from flask import Flask, render_template, request, jsonify
from pathlib import Path
import json
import subprocess

app = Flask(__name__)

CONTENT_DIR = Path("content")

# =========================
# UI
# =========================
@app.route("/")
def index():
    return render_template("editor.html")


# =========================
# API: list SKUs (for autocomplete)
# =========================
@app.route("/api/skus")
def list_skus():
    skus = sorted(p.stem for p in CONTENT_DIR.glob("*.json"))
    return jsonify(skus)


# =========================
# API: get product by SKU
# =========================
@app.route("/api/product/<sku>")
def get_product(sku):
    file = CONTENT_DIR / f"{sku}.json"
    if not file.exists():
        return jsonify({"error": "SKU not found"}), 404

    return json.loads(file.read_text(encoding="utf-8"))


# =========================
# API: save product language block
# =========================
@app.route("/api/product/<sku>", methods=["POST"])
def save_product(sku):
    file = CONTENT_DIR / f"{sku}.json"
    if not file.exists():
        return jsonify({"error": "SKU not found"}), 404

    data = request.json
    product = json.loads(file.read_text(encoding="utf-8"))

    lang = data["lang"]

    # 🔐 safety: ensure lang exists
    if lang not in product.get("i18n", {}):
        product.setdefault("i18n", {})[lang] = {}

    product["i18n"][lang]["description"] = data.get("description", "")
    product["i18n"][lang]["ingredients"] = data.get("ingredients", "")
    product["i18n"][lang]["precautions"] = data.get("precautions", "")
    product["i18n"][lang]["history"] = data.get("history", [])

    file.write_text(
        json.dumps(product, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    return jsonify({"status": "saved"})


# =========================
# API: rebuild HTML pages
# =========================
@app.route("/api/rebuild/<sku>", methods=["POST"])
def rebuild_html(sku):
    # пока rebuild всех страниц — для MVP ок
    subprocess.run(["python", "generate_pages.py"], check=True)
    return jsonify({"status": "rebuilt"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
