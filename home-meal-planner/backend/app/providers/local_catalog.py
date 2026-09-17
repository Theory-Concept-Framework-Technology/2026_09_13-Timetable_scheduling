"""Local JSON recipe catalog."""

from __future__ import annotations

import json
from typing import Dict, List, Optional

from app.config import RECIPES_MANIFEST
from app.food_images import resolve_recipe_image
from app.models import Ingredient, NutritionInfo, Recipe
from app.vegetarian import is_vegetarian_recipe


class LocalCatalogProvider:
    def __init__(self) -> None:
        self._recipes: Dict[str, Recipe] = {}
        self._load()

    def _load(self) -> None:
        if not RECIPES_MANIFEST.is_file():
            return
        raw = json.loads(RECIPES_MANIFEST.read_text(encoding="utf-8"))
        for item in raw:
            nutrition_raw = item.get("nutrition") or {}
            nutrition = NutritionInfo(
                calories=float(nutrition_raw.get("calories", 0)),
                protein_g=float(nutrition_raw.get("protein_g", 0)),
                carbohydrates_g=float(nutrition_raw.get("carbohydrates_g", 0)),
                fat_g=float(nutrition_raw.get("fat_g", 0)),
                source=nutrition_raw.get("source", "catalog"),
            )
            ingredients = [
                Ingredient(name=i.get("name", ""), measure=i.get("measure", ""))
                for i in item.get("ingredients", [])
            ]
            recipe = Recipe(
                id=item["id"],
                name=item["name"],
                image=resolve_recipe_image(
                    item["id"],
                    list(item.get("meal_types", [])),
                    item.get("image", ""),
                ),
                ingredients=ingredients,
                instructions=item.get("instructions", ""),
                preparation_time_min=int(item.get("preparation_time_min", 30)),
                servings=int(item.get("servings", 2)),
                meal_types=list(item.get("meal_types", [])),
                cuisine=item.get("cuisine", "Indian"),
                tags=list(item.get("tags", [])),
                nutrition=nutrition,
                source="local",
            )
            names = [ing.name for ing in recipe.ingredients]
            if is_vegetarian_recipe(recipe.name, names, recipe.instructions):
                self._recipes[recipe.id] = recipe

    def all_recipes(self) -> List[Recipe]:
        return list(self._recipes.values())

    def get_by_id(self, recipe_id: str) -> Optional[Recipe]:
        return self._recipes.get(recipe_id)

    def by_meal_type(self, meal_type: str) -> List[Recipe]:
        return [r for r in self._recipes.values() if meal_type in r.meal_types]

    def search(self, query: str, limit: int = 20) -> List[Recipe]:
        q = (query or "").strip().lower()
        results: List[Recipe] = []
        for recipe in self._recipes.values():
            if not q:
                results.append(recipe)
            else:
                hay = " ".join(
                    [recipe.name, recipe.cuisine, " ".join(recipe.meal_types), " ".join(recipe.tags)]
                ).lower()
                if q in hay or any(q in ing.name.lower() for ing in recipe.ingredients):
                    results.append(recipe)
            if len(results) >= limit:
                break
        return results[:limit]
