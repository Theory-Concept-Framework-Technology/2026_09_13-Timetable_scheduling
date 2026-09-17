"""Vegetarian filtering helpers."""

from __future__ import annotations

from typing import Iterable, List

from app.config import NON_VEGETARIAN_TERMS


def text_contains_non_veg(text: str) -> bool:
    lower = (text or "").lower()
    for term in NON_VEGETARIAN_TERMS:
        if term in lower:
            return True
    return False


def is_vegetarian_recipe(name: str, ingredients: Iterable[str], instructions: str = "") -> bool:
    blob = " ".join([name or ""] + list(ingredients) + [instructions or ""])
    return not text_contains_non_veg(blob)


def filter_vegetarian_names(names: List[str]) -> List[str]:
    return [n for n in names if not text_contains_non_veg(n)]
