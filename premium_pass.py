import json
from pathlib import Path

CONTENT_DIR = Path("content")

def enhance_description(desc, category):
    if not desc:
        return desc

    if len(desc) > 180:
        return desc  # уже достаточно плотное

    additions = {
        "WATER": "Carefully sourced and valued for its purity and everyday refreshment, it is well suited for daily hydration at home or on the go.",
        "CEREAL": "Prepared using traditional methods, this product is appreciated for its consistent quality and versatility in everyday home cooking.",
        "BEER": "Brewed with attention to balance and character, it reflects the heritage and craftsmanship associated with its style.",
        "PASTA": "Made to deliver reliable texture and taste, it is suitable for a wide range of classic and modern recipes."
    }

    extra = additions.get(category.upper(), "Valued for its consistent quality and suitability for everyday use.")
    return desc.strip() + " " + extra


def enhance_ingredients(ing):
    if not ing:
        return ing

    if len(ing) > 60:
        return ing

    return ing.strip() + " Commonly used in traditional recipes and everyday cooking."


def enhance_history(history, brand, category, country):
    if not history or len(history) >= 3:
        return history

    return [
        {
            "year": "Origins",
            "text": f"The {brand} brand originates from {country or 'its region of production'}, reflecting local traditions and expertise."
        },
        {
            "year": "Production",
            "text": f"Over time, {brand} has focused on maintaining consistent quality and careful production standards within the {category.lower()} category."
        },
        {
            "year": "Today",
            "text": f"Today, {brand} products are appreciated for their reliability and suitability for everyday use."
        }
    ]


updated = 0

for json_file in CONTENT_DIR.glob("*.json"):
    data = json.loads(json_file.read_text(encoding="utf-8"))
    i18n = data.get("i18n", {}).get("en", {})
    if not i18n:
        continue

    category = data.get("category", "")
    brand = data.get("brand", "the brand")
    country = data.get("country_of_origin", "")

    changed = False

    # --- Description ---
    desc = i18n.get("description", "")
    new_desc = enhance_description(desc, category)
    if new_desc != desc:
        i18n["description"] = new_desc
        changed = True

    # --- Ingredients ---
    ing = i18n.get("ingredients", "")
    new_ing = enhance_ingredients(ing)
    if new_ing != ing:
        i18n["ingredients"] = new_ing
        changed = True

    # --- History ---
    hist = i18n.get("history", [])
    new_hist = enhance_history(hist, brand, category, country)
    if new_hist != hist:
        i18n["history"] = new_hist
        changed = True

    if changed:
        json_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        updated += 1

print("✅ PREMIUM PASS completed")
print("Enhanced products:", updated)
