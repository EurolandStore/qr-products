def beer_description(brand, name, country):
    return (
        f"{brand} {name or 'Beer'} is crafted following traditional brewing methods that emphasize balance, "
        f"aroma, and depth of flavor. Its character reveals gentle malt sweetness, subtle bitterness, and "
        f"refined aromatic notes that unfold with every sip. Brewed in {country}, this beer reflects a long-standing "
        f"brewing heritage and attention to quality. Best enjoyed well chilled, it pairs beautifully with "
        f"grilled meats, cheeses, and classic pub dishes. A versatile choice for both casual enjoyment and "
        f"special moments."
    )


def pickled_description(brand, name, country):
    return (
        f"{brand} {name or 'Pickled Vegetables'} are prepared using time-honored recipes that preserve the natural "
        f"crunch, freshness, and vibrant character of carefully selected vegetables. Balanced acidity and aromatic "
        f"spices create a refreshing, tangy taste that complements a wide variety of dishes. Produced in {country}, "
        f"these pickled vegetables are perfect as a side dish, appetizer, or ingredient in traditional and modern "
        f"recipes. Their clean flavor and satisfying texture make them a staple in Mediterranean-inspired cuisine."
    )


def cheese_description(brand, name, country):
    return (
        f"{brand} {name or 'Cheese'} is produced using carefully selected milk and traditional cheesemaking "
        f"techniques that highlight its natural texture and rich flavor. Depending on the variety, it may offer "
        f"creamy, smooth notes or a firmer, more pronounced taste profile. Crafted in {country}, this cheese pairs "
        f"beautifully with fresh bread, fruits, wines, and a variety of dishes. A versatile ingredient that elevates "
        f"both everyday meals and special occasions."
    )


def sausage_description(brand, name, country):
    return (
        f"{brand} {name or 'Sausage'} is prepared following traditional recipes that emphasize seasoning balance "
        f"and authentic flavor. Carefully selected meats and spices create a satisfying texture and a rich, savory "
        f"taste. Produced in {country}, this sausage is ideal for grilling, pan-frying, or serving as part of a "
        f"charcuterie board. A flavorful addition to both classic and modern dishes."
    )


def sweets_description(brand, name, country):
    return (
        f"{brand} {name or 'Sweets'} are crafted to deliver a delightful balance of sweetness and texture. "
        f"Using quality ingredients and proven recipes, these treats offer a satisfying taste experience "
        f"for all ages. Made in {country}, they are perfect as a dessert, snack, or accompaniment to coffee "
        f"and tea. A pleasant indulgence for everyday enjoyment."
    )


def general_food_description(brand, name, country):
    return (
        f"{brand} {name or 'Food Product'} is produced with a focus on quality, consistency, and authentic taste. "
        f"Crafted in {country}, it reflects traditional culinary practices adapted for modern kitchens. "
        f"This product is suitable for everyday use and integrates easily into a wide range of recipes, "
        f"offering reliable flavor and convenience."
    )
