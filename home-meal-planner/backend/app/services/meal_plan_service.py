"""Search, filters, and nutrition summaries."""

from __future__ import annotations

from typing import List, Optional

from app.config import DEFAULT_CALORIE_TARGET, MEAL_DAYS, NUTRITION_DISCLAIMER
from app.models import (
    DailyNutritionSummary,
    MealPlan,
    MealSlot,
    RecipeSearchResult,
    SearchResponse,
    WeeklyNutritionSummary,
)
from app.providers.themealdb import CombinedRecipeService
from app.providers.usda_fdc import USDANutritionService
from app.db.repository import MealPlanRepository
from app.services.plan_generator import PlanGenerator


class MealPlanService:
    def __init__(self) -> None:
        self.repo = MealPlanRepository()
        self.recipes = CombinedRecipeService()
        self.nutrition = USDANutritionService()
        self.generator = PlanGenerator()

    def _hydrate_plan(self, plan: MealPlan) -> MealPlan:
        """Refresh slot names, images, and macros from the current recipe catalog."""
        refreshed: List[MealSlot] = []
        for slot in plan.slots:
            recipe = self.recipes.get_recipe(slot.recipe_id)
            if not recipe:
                refreshed.append(slot)
                continue
            enriched = self.nutrition.enrich_recipe(recipe.model_copy(deep=True))
            n = enriched.nutrition
            refreshed.append(
                slot.model_copy(
                    update={
                        "name": enriched.name,
                        "image": enriched.image or slot.image,
                        "calories": n.calories,
                        "protein_g": n.protein_g,
                        "carbohydrates_g": n.carbohydrates_g,
                        "fat_g": n.fat_g,
                        "nutrition_source": n.source,
                    }
                )
            )
        return plan.model_copy(update={"slots": refreshed})

    def _plan_is_stale(self, plan: MealPlan) -> bool:
        if not plan.slots:
            return True
        with_image = sum(1 for s in plan.slots if s.image and len(s.image) > 5)
        if with_image < len(plan.slots) // 2:
            return True
        unique_names = len({s.name for s in plan.slots})
        if unique_names < min(18, len(plan.slots) - 4):
            return True
        return False

    def get_or_create_plan(self) -> MealPlan:
        plan = self.repo.get_active_plan()
        if plan:
            plan = self._hydrate_plan(plan)
            if self._plan_is_stale(plan):
                return self.regenerate_plan()
            return plan
        plan = self.generator.generate()
        return self.repo.save_plan(plan)

    def regenerate_plan(self) -> MealPlan:
        plan = self.generator.generate(week_label="Generated plan")
        return self.repo.save_plan(plan)

    def search(
        self,
        query: str = "",
        meal_type: Optional[str] = None,
        cuisine: Optional[str] = None,
        max_time: Optional[int] = None,
        min_calories: Optional[float] = None,
        max_calories: Optional[float] = None,
        high_protein: bool = False,
    ) -> SearchResponse:
        raw = self.recipes.search(query, limit=40)
        results: List[RecipeSearchResult] = []
        for recipe in raw:
            enriched = self.nutrition.enrich_recipe(recipe.model_copy(deep=True))
            if meal_type and enriched.meal_types and meal_type not in enriched.meal_types:
                continue
            if cuisine:
                c = cuisine.lower()
                if c == "indian" and enriched.cuisine.lower() != "indian":
                    continue
                if c == "other" and enriched.cuisine.lower() == "indian":
                    continue
            if max_time is not None and enriched.preparation_time_min > max_time:
                continue
            cal = enriched.nutrition.calories
            if min_calories is not None and cal < min_calories:
                continue
            if max_calories is not None and cal > max_calories:
                continue
            if high_protein and enriched.nutrition.protein_g < 15:
                continue
            results.append(
                RecipeSearchResult(
                    id=enriched.id,
                    name=enriched.name,
                    image=enriched.image,
                    calories=enriched.nutrition.calories,
                    protein_g=enriched.nutrition.protein_g,
                    preparation_time_min=enriched.preparation_time_min,
                    meal_types=enriched.meal_types,
                    cuisine=enriched.cuisine,
                )
            )
        return SearchResponse(
            query=query,
            count=len(results),
            results=results,
            disclaimer=NUTRITION_DISCLAIMER,
        )

    def get_recipe_detail(self, recipe_id: str):
        recipe = self.recipes.get_recipe(recipe_id)
        if not recipe:
            return None
        enriched = self.nutrition.enrich_recipe(recipe.model_copy(deep=True))
        enriched.nutrition.disclaimer = NUTRITION_DISCLAIMER
        return enriched

    def daily_summary(self, plan: MealPlan, day: str) -> DailyNutritionSummary:
        day_slots = [s for s in plan.slots if s.day == day]
        meals = []
        total_cal = total_p = total_c = total_f = 0.0
        for slot in day_slots:
            meals.append(
                {
                    "meal_type": slot.meal_type,
                    "name": slot.name,
                    "calories": slot.calories,
                    "protein_g": slot.protein_g,
                    "carbohydrates_g": slot.carbohydrates_g,
                    "fat_g": slot.fat_g,
                    "meal_time": slot.meal_time,
                    "image": slot.image,
                    "recipe_id": slot.recipe_id,
                }
            )
            total_cal += slot.calories
            total_p += slot.protein_g
            total_c += slot.carbohydrates_g
            total_f += slot.fat_g
        return DailyNutritionSummary(
            day=day,
            meals=meals,
            total_calories=round(total_cal, 1),
            total_protein_g=round(total_p, 1),
            total_carbohydrates_g=round(total_c, 1),
            total_fat_g=round(total_f, 1),
            calorie_target=DEFAULT_CALORIE_TARGET,
            disclaimer=NUTRITION_DISCLAIMER,
        )

    def weekly_summary(self, plan: MealPlan) -> WeeklyNutritionSummary:
        days = [self.daily_summary(plan, day) for day in MEAL_DAYS]
        total_cal = sum(d.total_calories for d in days)
        return WeeklyNutritionSummary(
            days=days,
            total_calories=round(total_cal, 1),
            disclaimer=NUTRITION_DISCLAIMER,
        )

    def today_day_name(self) -> str:
        import datetime

        index = datetime.date.today().weekday()
        if index < len(MEAL_DAYS):
            return MEAL_DAYS[index]
        return MEAL_DAYS[0]
