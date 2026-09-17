"""Home Meal Planner — configuration."""

from __future__ import annotations

import os
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

DATA_DIR = BACKEND_DIR / "data"
RECIPES_MANIFEST = DATA_DIR / "recipes.json"

MEAL_DAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

MEAL_TYPES = ("breakfast", "lunch", "snack", "dinner")

MEAL_TYPE_LABELS = {
    "breakfast": "Breakfast",
    "lunch": "Lunch",
    "snack": "Snack",
    "dinner": "Dinner",
}

MEAL_DEFAULT_TIMES = {
    "breakfast": "08:00",
    "lunch": "13:00",
    "snack": "17:00",
    "dinner": "20:00",
}

NON_VEGETARIAN_TERMS = (
    "chicken",
    "fish",
    "mutton",
    "lamb",
    "beef",
    "pork",
    "bacon",
    "ham",
    "sausage",
    "shrimp",
    "prawn",
    "salmon",
    "tuna",
    "egg",
    "eggs",
    "omelette",
    "omelet",
    "seafood",
    "anchovy",
    "crab",
    "lobster",
)

THEMEALDB_BASE = "https://www.themealdb.com/api/json/v1"
USDA_FDC_BASE = "https://api.nal.usda.gov/fdc/v1"

MEAL_DB_PATH = Path(os.environ.get("MEAL_DB_PATH", str(PROJECT_ROOT / "data" / "meals.db")))
MEAL_CACHE_DIR = Path(os.environ.get("MEAL_CACHE_DIR", str(PROJECT_ROOT / "data" / "meal_cache")))

THEMEALDB_API_KEY = os.environ.get("THEMEALDB_API_KEY", "1")
USDA_FDC_API_KEY = os.environ.get("USDA_FDC_API_KEY", "")

HTTP_CACHE_TTL_SECONDS = 86400

NUTRITION_DISCLAIMER = (
    "Nutrition values are approximate estimates and may vary based on "
    "serving size, ingredients, and preparation."
)

DEFAULT_CALORIE_TARGET = 2000
