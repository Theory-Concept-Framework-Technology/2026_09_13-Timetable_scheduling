"""FastAPI application for Home Meal Planner."""

from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import NUTRITION_DISCLAIMER
from app.services.meal_plan_service import MealPlanService

app = FastAPI(title="Home Meal Planner API", version="1.0.0")
service = MealPlanService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/meals/health")
def health():
    return {"status": "ok", "service": "meal-api"}


@app.get("/api/meals/plans/current")
def get_current_plan():
    plan = service.get_or_create_plan()
    weekly = service.weekly_summary(plan)
    today = service.today_day_name()
    daily = service.daily_summary(plan, today)
    return {
        "plan": plan.model_dump(),
        "today": today,
        "daily": daily.model_dump(),
        "weekly_nutrition": weekly.model_dump(),
        "disclaimer": NUTRITION_DISCLAIMER,
    }


@app.post("/api/meals/plans/generate")
def generate_plan():
    plan = service.regenerate_plan()
    weekly = service.weekly_summary(plan)
    return {
        "plan": plan.model_dump(),
        "weekly_nutrition": weekly.model_dump(),
        "disclaimer": NUTRITION_DISCLAIMER,
    }


@app.get("/api/meals/plans/nutrition/daily")
def daily_nutrition(day: Optional[str] = None):
    plan = service.get_or_create_plan()
    target_day = day or service.today_day_name()
    return service.daily_summary(plan, target_day).model_dump()


@app.get("/api/meals/plans/nutrition/weekly")
def weekly_nutrition():
    plan = service.get_or_create_plan()
    return service.weekly_summary(plan).model_dump()


@app.get("/api/meals/search")
def search_recipes(
    q: str = Query("", alias="q"),
    meal_type: Optional[str] = None,
    cuisine: Optional[str] = None,
    max_time: Optional[int] = None,
    min_calories: Optional[float] = None,
    max_calories: Optional[float] = None,
    high_protein: bool = False,
):
    return service.search(
        query=q,
        meal_type=meal_type,
        cuisine=cuisine,
        max_time=max_time,
        min_calories=min_calories,
        max_calories=max_calories,
        high_protein=high_protein,
    ).model_dump()


@app.get("/api/meals/recipes/{recipe_id}")
def get_recipe(recipe_id: str):
    recipe = service.get_recipe_detail(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe.model_dump()
