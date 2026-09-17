"""Pydantic models for Home Meal Planner."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

NutritionSource = Literal["catalog", "api", "estimated", "mixed"]


class NutritionInfo(BaseModel):
    calories: float = 0
    protein_g: float = 0
    carbohydrates_g: float = 0
    fat_g: float = 0
    source: NutritionSource = "catalog"
    disclaimer: str = ""


class Ingredient(BaseModel):
    name: str
    measure: str = ""


class Recipe(BaseModel):
    id: str
    name: str
    image: str = ""
    ingredients: List[Ingredient] = Field(default_factory=list)
    instructions: str = ""
    preparation_time_min: int = 30
    servings: int = 2
    meal_types: List[str] = Field(default_factory=list)
    cuisine: str = "Indian"
    tags: List[str] = Field(default_factory=list)
    nutrition: NutritionInfo = Field(default_factory=NutritionInfo)
    source: str = "local"
    external_id: Optional[str] = None


class MealSlot(BaseModel):
    id: Optional[int] = None
    day: str
    meal_type: str
    recipe_id: str
    name: str
    image: str = ""
    serving_size: float = 1.0
    meal_time: str = ""
    calories: float = 0
    protein_g: float = 0
    carbohydrates_g: float = 0
    fat_g: float = 0
    nutrition_source: NutritionSource = "catalog"


class MealPlan(BaseModel):
    id: str
    week_label: str
    slots: List[MealSlot] = Field(default_factory=list)


class DailyNutritionSummary(BaseModel):
    day: str
    meals: List[Dict[str, Any]]
    total_calories: float
    total_protein_g: float
    total_carbohydrates_g: float
    total_fat_g: float
    calorie_target: float = 2000
    disclaimer: str


class WeeklyNutritionSummary(BaseModel):
    days: List[DailyNutritionSummary]
    total_calories: float
    disclaimer: str


class RecipeSearchResult(BaseModel):
    id: str
    name: str
    image: str = ""
    calories: float = 0
    protein_g: float = 0
    preparation_time_min: int = 0
    meal_types: List[str] = Field(default_factory=list)
    cuisine: str = ""


class SearchResponse(BaseModel):
    query: str
    count: int
    results: List[RecipeSearchResult]
    disclaimer: str = ""
