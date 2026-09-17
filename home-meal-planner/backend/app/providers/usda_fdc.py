"""USDA FoodData Central nutrition enrichment."""

from __future__ import annotations

from typing import Optional

import httpx

from app.cache.file_cache import FileCache
from app.config import NUTRITION_DISCLAIMER, USDA_FDC_API_KEY, USDA_FDC_BASE
from app.models import NutritionInfo, Recipe


NUTRIENT_IDS = {
    "calories": 1008,
    "protein": 1003,
    "carbs": 1005,
    "fat": 1004,
}


class USDANutritionService:
    def __init__(self, cache: Optional[FileCache] = None) -> None:
        self.api_key = USDA_FDC_API_KEY
        self.cache = cache or FileCache()

    def available(self) -> bool:
        return bool(self.api_key)

    def _search_food(self, query: str) -> Optional[dict]:
        if not self.api_key:
            return None
        cache_key = f"usda-search:{query}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        url = f"{USDA_FDC_BASE}/foods/search"
        params = {
            "api_key": self.api_key,
            "query": query,
            "pageSize": 1,
            "dataType": "Foundation,SR Legacy",
        }
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(url, params=params)
                if response.status_code == 429:
                    return None
                response.raise_for_status()
                data = response.json()
                foods = data.get("foods") or []
                if not foods:
                    return None
                top = foods[0]
                self.cache.set(cache_key, top)
                return top
        except httpx.HTTPError:
            return None

    def _nutrient_value(self, food: dict, nutrient_id: int) -> float:
        for item in food.get("foodNutrients") or []:
            if item.get("nutrientId") == nutrient_id or item.get("nutrientNumber") == str(nutrient_id):
                return float(item.get("value") or 0)
        return 0.0

    def estimate_for_recipe(self, recipe: Recipe) -> NutritionInfo:
        if recipe.nutrition.source == "catalog" and recipe.nutrition.calories > 0:
            recipe.nutrition.disclaimer = NUTRITION_DISCLAIMER
            return recipe.nutrition

        if not self.available():
            if recipe.nutrition.calories <= 0:
                recipe.nutrition.source = "estimated"
            recipe.nutrition.disclaimer = NUTRITION_DISCLAIMER
            return recipe.nutrition

        totals = NutritionInfo(source="api", disclaimer=NUTRITION_DISCLAIMER)
        counted = 0
        for ing in recipe.ingredients[:5]:
            food = self._search_food(ing.name)
            if not food:
                continue
            factor = 0.5
            totals.calories += self._nutrient_value(food, NUTRIENT_IDS["calories"]) * factor
            totals.protein_g += self._nutrient_value(food, NUTRIENT_IDS["protein"]) * factor
            totals.carbohydrates_g += self._nutrient_value(food, NUTRIENT_IDS["carbs"]) * factor
            totals.fat_g += self._nutrient_value(food, NUTRIENT_IDS["fat"]) * factor
            counted += 1

        if counted == 0:
            totals.source = "estimated"
            return recipe.nutrition if recipe.nutrition.calories > 0 else totals

        totals.calories = round(totals.calories, 1)
        totals.protein_g = round(totals.protein_g, 1)
        totals.carbohydrates_g = round(totals.carbohydrates_g, 1)
        totals.fat_g = round(totals.fat_g, 1)
        return totals

    def enrich_recipe(self, recipe: Recipe) -> Recipe:
        nutrition = self.estimate_for_recipe(recipe)
        recipe.nutrition = nutrition
        return recipe
