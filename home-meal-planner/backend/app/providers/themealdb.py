"""TheMealDB API client (optional enrichment)."""

from __future__ import annotations

from typing import List, Optional
from urllib.parse import quote

import httpx

from app.cache.file_cache import FileCache
from app.config import THEMEALDB_API_KEY, THEMEALDB_BASE
from app.models import Ingredient, NutritionInfo, Recipe
from app.vegetarian import is_vegetarian_recipe, text_contains_non_veg
from app.providers.local_catalog import LocalCatalogProvider


class TheMealDBProvider:
    def __init__(self, cache: Optional[FileCache] = None) -> None:
        self.api_key = THEMEALDB_API_KEY or "1"
        self.base = f"{THEMEALDB_BASE}/{self.api_key}"
        self.cache = cache or FileCache()

    def _get_json(self, url: str) -> dict:
        cached = self.cache.get(url)
        if cached is not None:
            return cached
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                self.cache.set(url, data)
                return data
        except (httpx.HTTPError, ValueError):
            return {}

    def _parse_meal(self, meal: dict) -> Optional[Recipe]:
        if not meal:
            return None
        name = meal.get("strMeal") or ""
        ingredients: List[Ingredient] = []
        for i in range(1, 21):
            ing = (meal.get(f"strIngredient{i}") or "").strip()
            measure = (meal.get(f"strMeasure{i}") or "").strip()
            if ing:
                ingredients.append(Ingredient(name=ing, measure=measure))
        ing_names = [i.name for i in ingredients]
        if not is_vegetarian_recipe(name, ing_names, meal.get("strInstructions") or ""):
            return None
        external_id = meal.get("idMeal")
        return Recipe(
            id=f"themealdb-{external_id}",
            name=name,
            image=meal.get("strMealThumb") or "",
            ingredients=ingredients,
            instructions=meal.get("strInstructions") or "",
            preparation_time_min=45,
            servings=2,
            meal_types=[],
            cuisine=meal.get("strArea") or "Other",
            tags=(meal.get("strTags") or "").split(",") if meal.get("strTags") else [],
            nutrition=NutritionInfo(source="estimated"),
            source="themealdb",
            external_id=str(external_id),
        )

    def lookup(self, external_id: str) -> Optional[Recipe]:
        url = f"{self.base}/lookup.php?i={external_id}"
        data = self._get_json(url)
        meals = data.get("meals") or []
        if not meals:
            return None
        return self._parse_meal(meals[0])

    def search(self, query: str, limit: int = 12) -> List[Recipe]:
        q = (query or "").strip()
        if not q or text_contains_non_veg(q):
            return []
        url = f"{self.base}/search.php?s={quote(q)}"
        data = self._get_json(url)
        meals = data.get("meals") or []
        results: List[Recipe] = []
        for meal in meals:
            parsed = self._parse_meal(meal)
            if parsed:
                results.append(parsed)
            if len(results) >= limit:
                break
        return results

    def get_by_id(self, recipe_id: str) -> Optional[Recipe]:
        if not recipe_id.startswith("themealdb-"):
            return None
        external_id = recipe_id.replace("themealdb-", "", 1)
        return self.lookup(external_id)


class CombinedRecipeService:
    """Local catalog first; TheMealDB for external IDs and search augmentation."""

    def __init__(self) -> None:
        self.local = LocalCatalogProvider()
        self.themealdb = TheMealDBProvider()

    def get_recipe(self, recipe_id: str) -> Optional[Recipe]:
        local = self.local.get_by_id(recipe_id)
        if local:
            return local
        return self.themealdb.get_by_id(recipe_id)

    def search(self, query: str, limit: int = 24) -> List[Recipe]:
        seen = set()
        merged: List[Recipe] = []
        for recipe in self.local.search(query, limit=limit):
            if recipe.id not in seen:
                seen.add(recipe.id)
                merged.append(recipe)
        if len(merged) < limit:
            for recipe in self.themealdb.search(query, limit=limit - len(merged)):
                if recipe.id not in seen:
                    seen.add(recipe.id)
                    merged.append(recipe)
        return merged[:limit]

    def recipes_for_meal_type(self, meal_type: str) -> List[Recipe]:
        return self.local.by_meal_type(meal_type)
