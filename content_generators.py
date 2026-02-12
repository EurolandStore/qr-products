from copy import deepcopy

# -----------------------------------
# SECTION TITLES
# -----------------------------------
SECTION_TITLES = {
    "en": {
        "description_title": "Description",
        "ingredients_title": "Ingredients",
        "precautions_title": "Consumption precautions",
        "history_title": "History"
    },
    "ru": {
        "description_title": "Описание",
        "ingredients_title": "Ингредиенты",
        "precautions_title": "Предостережения",
        "history_title": "История"
    },
    "ua": {
        "description_title": "Опис",
        "ingredients_title": "Інгредієнти",
        "precautions_title": "Застереження",
        "history_title": "Історія"
    },
    "de": {
        "description_title": "Beschreibung",
        "ingredients_title": "Zutaten",
        "precautions_title": "Hinweise",
        "history_title": "Geschichte"
    },
    "es": {
        "description_title": "Descripción",
        "ingredients_title": "Ingredientes",
        "precautions_title": "Advertencias",
        "history_title": "Historia"
    },
    "it": {
        "description_title": "Descrizione",
        "ingredients_title": "Ingredienti",
        "precautions_title": "Avvertenze",
        "history_title": "Storia"
    },
    "hr": {
        "description_title": "Opis",
        "ingredients_title": "Sastojci",
        "precautions_title": "Upozorenja",
        "history_title": "Povijest"
    },
    "hu": {
        "description_title": "Leírás",
        "ingredients_title": "Összetevők",
        "precautions_title": "Figyelmeztetések",
        "history_title": "Történet"
    }
}

# -----------------------------------
# TEXT TEMPLATES
# -----------------------------------
TEXT = {
    "en": {
        "description": "{title} is produced using traditional methods. Made in {country}, it reflects the heritage and expertise of the brand.",
        "ingredients": "Ingredients may vary depending on the product. Please refer to the packaging for details.",
        "precautions": "Store according to package instructions. Check the label for allergen information.",
        "history": [
            ("Origins", "The {brand} brand was founded in {country}."),
            ("Development", "Over time, {brand} expanded its range."),
            ("Today", "Today, {brand} products are enjoyed worldwide.")
        ]
    },
    "ru": {
        "description": "{title} производится с использованием традиционных методов. Произведено в {country}, отражает экспертизу бренда.",
        "ingredients": "Состав может отличаться в зависимости от продукта. Подробную информацию смотрите на упаковке.",
        "precautions": "Хранить в соответствии с указаниями на упаковке. Проверьте информацию об аллергенах.",
        "history": [
            ("Истоки", "Бренд {brand} был основан в {country}."),
            ("Развитие", "Со временем бренд {brand} расширил ассортимент."),
            ("Сегодня", "Сегодня продукция бренда {brand} известна во многих странах.")
        ]
    },
    "ua": {
        "description": "{title} виготовляється з використанням традиційних методів. Вироблено в {country}, відображає експертизу бренду.",
        "ingredients": "Склад може відрізнятися залежно від продукту. Детальну інформацію дивіться на упаковці.",
        "precautions": "Зберігати відповідно до інструкцій на упаковці. Перевірте інформацію про алергени.",
        "history": [
            ("Походження", "Бренд {brand} був заснований у {country}."),
            ("Розвиток", "З часом бренд {brand} розширив асортимент."),
            ("Сьогодні", "Сьогодні продукція бренду {brand} відома у багатьох країнах.")
        ]
    }
}

# -----------------------------------
# EN = SOURCE OF TRUTH
# -----------------------------------
def generate_en_content(product, en_block):
    title = product.get("name", "").strip() or product.get("brand", "")
    brand = product.get("brand", "")
    country = product.get("country_of_origin", "")

    en_block.update({
        "title": title,
        "sections": SECTION_TITLES["en"],
        "description": TEXT["en"]["description"].format(title=title, country=country),
        "ingredients": TEXT["en"]["ingredients"],
        "precautions": TEXT["en"]["precautions"],
        "history": [
            {"year": y, "text": t.format(brand=brand, country=country)}
            for y, t in TEXT["en"]["history"]
        ]
    })
    return en_block


# -----------------------------------
# I18N GENERATION
# -----------------------------------
def generate_i18n_from_en(data):
    en = data["i18n"]["en"]
    brand = data.get("brand", "")
    country = data.get("country_of_origin", "")
    title = en["title"]

    for lang in ["ru", "ua", "de", "es", "it", "hr", "hu"]:
        block = deepcopy(en)
        block["title"] = title
        block["sections"] = SECTION_TITLES[lang]

        base = TEXT.get(lang, TEXT["en"])
        block["description"] = base["description"].format(title=title, country=country)
        block["ingredients"] = base["ingredients"]
        block["precautions"] = base["precautions"]
        block["history"] = [
            {"year": y, "text": t.format(brand=brand, country=country)}
            for y, t in base["history"]
        ]

        data["i18n"][lang] = block
