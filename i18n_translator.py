import i18n_translator
print("i18n_translator loaded from:", i18n_translator.__file__)
from copy import deepcopy

LANGS = ["ru", "ua", "de", "es", "it", "hr", "hu"]

SECTION_TITLES = {
    "ru": {"description_title":"Описание","ingredients_title":"Ингредиенты","precautions_title":"Предостережения","history_title":"История"},
    "ua": {"description_title":"Опис","ingredients_title":"Інгредієнти","precautions_title":"Застереження","history_title":"Історія"},
    "de": {"description_title":"Beschreibung","ingredients_title":"Zutaten","precautions_title":"Hinweise","history_title":"Geschichte"},
    "es": {"description_title":"Descripción","ingredients_title":"Ingredientes","precautions_title":"Advertencias","history_title":"Historia"},
    "it": {"description_title":"Descrizione","ingredients_title":"Ingredienti","precautions_title":"Avvertenze","history_title":"Storia"},
    "hr": {"description_title":"Opis","ingredients_title":"Sastojci","precautions_title":"Upozorenja","history_title":"Povijest"},
    "hu": {"description_title":"Leírás","ingredients_title":"Összetevők","precautions_title":"Figyelmeztetések","history_title":"Történet"},
}

META_LABELS = {
    "ru": {"brand":"Бренд","country_of_origin":"Страна происхождения","category":"Категория","size":"Размер","alcohol_content":"Содержание алкоголя","sku":"SKU"},
    "ua": {"brand":"Бренд","country_of_origin":"Країна походження","category":"Категорія","size":"Розмір","alcohol_content":"Вміст алкоголю","sku":"SKU"},
    "de": {"brand":"Marke","country_of_origin":"Herkunftsland","category":"Kategorie","size":"Größe","alcohol_content":"Alkoholgehalt","sku":"SKU"},
    "es": {"brand":"Marca","country_of_origin":"País de origen","category":"Categoría","size":"Tamaño","alcohol_content":"Graduación alcohólica","sku":"SKU"},
    "it": {"brand":"Marca","country_of_origin":"Paese d'origine","category":"Categoria","size":"Formato","alcohol_content":"Contenuto alcolico","sku":"SKU"},
    "hr": {"brand":"Brend","country_of_origin":"Zemlja podrijetla","category":"Kategorija","size":"Veličina","alcohol_content":"Sadržaj alkohola","sku":"SKU"},
    "hu": {"brand":"Márka","country_of_origin":"Származási ország","category":"Kategória","size":"Méret","alcohol_content":"Alkoholtartalom","sku":"SKU"},
}

# 🔥 ШАБЛОНЫ ОПИСАНИЯ (чтобы НЕ было английского)
DESC_TPL = {
    "ru": "{name} — продукт бренда {brand}, произведённый в {country}. Изготовлен традиционными методами и отличается стабильным качеством. Удобный формат {size} подходит как для повседневного использования, так и для особых случаев.",
    "ua": "{name} — продукт бренду {brand}, виготовлений у {country}. Створений традиційними методами та вирізняється стабільною якістю. Зручний формат {size} підходить і для щоденного використання, і для особливих моментів.",
    "de": "{name} ist ein Produkt der Marke {brand} aus {country}. Nach traditionellen Methoden hergestellt und für gleichbleibende Qualität bekannt. Das Format {size} eignet sich sowohl für den Alltag als auch für besondere Anlässe.",
    "es": "{name} es un producto de la marca {brand} elaborado en {country}. Se produce con métodos tradicionales y destaca por su calidad constante. Su formato {size} es ideal para el día a día y ocasiones especiales.",
    "it": "{name} è un prodotto del marchio {brand} realizzato in {country}. Prodotto con metodi tradizionali e noto per la qualità costante. Il formato {size} è perfetto sia per l’uso quotidiano sia per le occasioni speciali.",
    "hr": "{name} je proizvod brenda {brand} proizveden u {country}. Izrađen tradicionalnim metodama i poznat po ujednačenoj kvaliteti. Format {size} prikladan je za svakodnevnu upotrebu i posebne prilike.",
    "hu": "A(z) {name} a {brand} márka terméke {country} területéről. Hagyományos eljárással készül, megbízható minőséggel. A(z) {size} kiszerelés a mindennapokra és különleges alkalmakra is ideális.",
}

ING_TEXT = {
    "ru":"Состав может отличаться в зависимости от продукта. См. упаковку.",
    "ua":"Склад може відрізнятися залежно від продукту. Див. упаковку.",
    "de":"Die Zutaten können je nach Produkt variieren. Siehe Verpackung.",
    "es":"Los ingredientes pueden variar según el producto. Consulte el envase.",
    "it":"Gli ingredienti possono variare a seconda del prodotto. Vedi confezione.",
    "hr":"Sastojci se mogu razlikovati ovisno o proizvodu. Pogledajte pakiranje.",
    "hu":"Az összetevők termékenként eltérhetnek. Lásd a csomagolást.",
}

PREC_TEXT = {
    "ru":"Хранить согласно указаниям на упаковке. Проверьте аллергенную информацию.",
    "ua":"Зберігати згідно з інструкціями на упаковці. Перевірте алергени.",
    "de":"Gemäß den Anweisungen auf der Verpackung lagern. Allergenhinweise prüfen.",
    "es":"Conservar según las instrucciones del envase. Verifique alérgenos.",
    "it":"Conservare secondo le istruzioni sulla confezione. Verificare allergeni.",
    "hr":"Čuvati prema uputama na pakiranju. Provjeriti alergene.",
    "hu":"A csomagolás szerint tárolandó. Ellenőrizze az allergéneket.",
}

HIST_TPL = {
    "ru":[
        "Бренд {brand} был основан в {country}.",
        "Со временем бренд {brand} расширил ассортимент.",
        "Сегодня продукция {brand} известна и любима во многих странах."
    ],
    "ua":[
        "Бренд {brand} був заснований у {country}.",
        "З часом бренд {brand} розширив асортимент.",
        "Сьогодні продукція {brand} відома у багатьох країнах."
    ],
    "de":[
        "Die Marke {brand} wurde in {country} gegründet.",
        "Im Laufe der Zeit erweiterte {brand} sein Sortiment.",
        "Heute werden {brand} Produkte weltweit geschätzt."
    ],
    "es":[
        "La marca {brand} fue fundada en {country}.",
        "Con el tiempo, {brand} amplió su gama de productos.",
        "Hoy, los productos {brand} se disfrutan en todo el mundo."
    ],
    "it":[
        "Il marchio {brand} è stato fondato in {country}.",
        "Nel tempo, {brand} ha ampliato la sua gamma.",
        "Oggi i prodotti {brand} sono apprezzati in tutto il mondo."
    ],
    "hr":[
        "Marka {brand} osnovana je u {country}.",
        "S vremenom je {brand} proširio svoj asortiman.",
        "Danas se proizvodi {brand} koriste diljem svijeta."
    ],
    "hu":[
        "A {brand} márkát {country} területén alapították.",
        "Idővel a {brand} kibővítette termékkínálatát.",
        "Ma a {brand} termékeket világszerte élvezik."
    ],
}

def generate_i18n_from_en(data: dict):
    en = data["i18n"]["en"]

    name = (data.get("name") or en.get("title") or "").strip()
    brand = (data.get("brand") or "").strip()
    country = (data.get("country_of_origin") or "").strip()
    size = (data.get("size") or "").strip()

    # EN остаётся как есть (его генерирует content_generators)
    for lang in LANGS:
        block = deepcopy(en)

        # labels
        block["sections"] = SECTION_TITLES[lang]
        block["meta"] = META_LABELS[lang]

        # title: оставляем товарное название, НЕ переводим
        block["title"] = name

        # description: делаем локализованный шаблон (без английского)
        block["description"] = DESC_TPL[lang].format(
            name=name, brand=brand, country=country, size=size
        )

        # ingredients/precautions: локализованные заглушки
        block["ingredients"] = ING_TEXT[lang]
        block["precautions"] = PREC_TEXT[lang]

        # history: локализованный шаблон + сохраняем годы из EN
        history_out = []
        years = [h.get("year", "") for h in en.get("history", [])]
        for i, tpl in enumerate(HIST_TPL[lang]):
            history_out.append({
                "year": years[i] if i < len(years) else "",
                "text": tpl.format(brand=brand, country=country)
            })
        block["history"] = history_out

        data["i18n"][lang] = block
