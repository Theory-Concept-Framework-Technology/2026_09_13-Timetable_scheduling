"""Abstract provider interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from app.models import Recipe


class RecipeProvider(ABC):
    @abstractmethod
    def get_by_id(self, recipe_id: str) -> Optional[Recipe]:
        ...

    @abstractmethod
    def search(self, query: str, limit: int = 20) -> List[Recipe]:
        ...
