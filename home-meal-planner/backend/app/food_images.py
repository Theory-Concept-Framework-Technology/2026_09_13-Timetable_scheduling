"""Food imagery — local SVG paths (always load) + optional Unsplash extras."""

from __future__ import annotations

MEAL_TYPE_ASSETS = {
    "breakfast": "/assets/meals/breakfast.svg",
    "lunch": "/assets/meals/lunch.svg",
    "snack": "/assets/meals/snack.svg",
    "dinner": "/assets/meals/dinner.svg",
}

RECIPE_IMAGES = {
    "local-poha": "/assets/meals/breakfast.svg",
    "local-upma": "/assets/meals/breakfast.svg",
    "local-idli": "/assets/meals/breakfast.svg",
    "local-dosa": "/assets/meals/breakfast.svg",
    "local-paratha": "/assets/meals/breakfast.svg",
    "local-oats": "/assets/meals/breakfast.svg",
    "local-uttapam": "/assets/meals/breakfast.svg",
    "local-chilla": "/assets/meals/breakfast.svg",
    "local-pongal": "/assets/meals/breakfast.svg",
    "local-sabudana": "/assets/meals/breakfast.svg",
    "local-dhokla": "/assets/meals/snack.svg",
    "local-dal-rice": "/assets/meals/lunch.svg",
    "local-rajma": "/assets/meals/lunch.svg",
    "local-chole": "/assets/meals/lunch.svg",
    "local-khichdi": "/assets/meals/lunch.svg",
    "local-lemon-rice": "/assets/meals/lunch.svg",
    "local-sambar-rice": "/assets/meals/lunch.svg",
    "local-methi-dal": "/assets/meals/lunch.svg",
    "local-mixed-veg": "/assets/meals/lunch.svg",
    "local-paneer": "/assets/meals/dinner.svg",
    "local-pulao": "/assets/meals/dinner.svg",
    "local-roti-dal": "/assets/meals/dinner.svg",
    "local-palak-paneer": "/assets/meals/dinner.svg",
    "local-biryani-veg": "/assets/meals/dinner.svg",
    "local-baingan": "/assets/meals/dinner.svg",
    "local-fruit": "/assets/meals/snack.svg",
    "local-sprouts": "/assets/meals/snack.svg",
    "local-curd": "/assets/meals/snack.svg",
    "local-nuts": "/assets/meals/snack.svg",
    "local-lassi": "/assets/meals/snack.svg",
    "local-salad": "/assets/meals/snack.svg",
    "local-chana-salad": "/assets/meals/snack.svg",
}


def resolve_recipe_image(recipe_id: str, meal_types: list, existing: str = "") -> str:
    if existing and existing.startswith("/assets/"):
        return existing
    if recipe_id in RECIPE_IMAGES:
        return RECIPE_IMAGES[recipe_id]
    for meal_type in meal_types:
        if meal_type in MEAL_TYPE_ASSETS:
            return MEAL_TYPE_ASSETS[meal_type]
    return "/assets/meals/default.svg"
