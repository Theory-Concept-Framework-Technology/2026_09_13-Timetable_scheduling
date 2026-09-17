"""Deterministic weekly vegetarian meal plan generator with variety."""

from __future__ import annotations

import random
import secrets
from typing import Dict, List, Set
from uuid import uuid4

from app.config import MEAL_DAYS, MEAL_DEFAULT_TIMES, MEAL_TYPES
from app.models import MealPlan, MealSlot, Recipe
from app.providers.themealdb import CombinedRecipeService
from app.providers.usda_fdc import USDANutritionService


class PlanGenerator:
    def __init__(self) -> None:
        self.recipes = CombinedRecipeService()
        self.nutrition = USDANutritionService()
        self._shuffle_seed = 0

    def _pool_for_type(self, meal_type: str) -> List[Recipe]:
        pool = self.recipes.recipes_for_meal_type(meal_type)
        if pool:
            return sorted(pool, key=lambda r: r.id)
        return sorted(self.recipes.local.all_recipes(), key=lambda r: r.id)

    def _pick_recipe(
        self,
        meal_type: str,
        day_index: int,
        used_by_type: Dict[str, Set[str]],
        prev_day_same_type: Dict[str, str],
    ) -> Recipe:
        pool = self._pool_for_type(meal_type)
        if not pool:
            raise ValueError("No recipes available for meal plan generation")

        rng = random.Random(self._shuffle_seed + day_index * 31 + hash(meal_type))
        pool = pool[:]
        rng.shuffle(pool)

        used = used_by_type.setdefault(meal_type, set())

        for candidate in pool:
            if candidate.id in used:
                continue
            if prev_day_same_type.get(meal_type) == candidate.id:
                continue
            used.add(candidate.id)
            prev_day_same_type[meal_type] = candidate.id
            return candidate

        for candidate in pool:
            if prev_day_same_type.get(meal_type) != candidate.id:
                prev_day_same_type[meal_type] = candidate.id
                return candidate

        candidate = pool[day_index % len(pool)]
        prev_day_same_type[meal_type] = candidate.id
        return candidate

    def _recipe_to_slot(self, day: str, meal_type: str, recipe: Recipe) -> MealSlot:
        enriched = self.nutrition.enrich_recipe(recipe.model_copy(deep=True))
        n = enriched.nutrition
        return MealSlot(
            day=day,
            meal_type=meal_type,
            recipe_id=enriched.id,
            name=enriched.name,
            image=enriched.image,
            serving_size=1.0,
            meal_time=MEAL_DEFAULT_TIMES.get(meal_type, ""),
            calories=n.calories,
            protein_g=n.protein_g,
            carbohydrates_g=n.carbohydrates_g,
            fat_g=n.fat_g,
            nutrition_source=n.source,
        )

    def generate(self, week_label: str = "This week") -> MealPlan:
        self._shuffle_seed = int(secrets.token_hex(4), 16)
        used_by_type: Dict[str, Set[str]] = {t: set() for t in MEAL_TYPES}
        prev_day_same_type: Dict[str, str] = {}
        slots: List[MealSlot] = []
        for day_index, day in enumerate(MEAL_DAYS):
            for meal_type in MEAL_TYPES:
                recipe = self._pick_recipe(meal_type, day_index, used_by_type, prev_day_same_type)
                slots.append(self._recipe_to_slot(day, meal_type, recipe))
        return MealPlan(id=str(uuid4()), week_label=week_label, slots=slots)
