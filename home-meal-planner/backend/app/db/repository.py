"""SQLite persistence for meal plans."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from app.config import MEAL_DB_PATH
from app.models import MealPlan, MealSlot


class MealPlanRepository:
    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = db_path or MEAL_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS meal_plans (
                    id TEXT PRIMARY KEY,
                    week_label TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS meal_slots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_id TEXT NOT NULL,
                    day TEXT NOT NULL,
                    meal_type TEXT NOT NULL,
                    recipe_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    FOREIGN KEY(plan_id) REFERENCES meal_plans(id)
                )
                """
            )
            conn.commit()

    def get_active_plan(self) -> Optional[MealPlan]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, week_label FROM meal_plans WHERE is_active = 1 ORDER BY created_at DESC LIMIT 1"
            ).fetchone()
            if not row:
                return None
            slots = self._load_slots(conn, row["id"])
            return MealPlan(id=row["id"], week_label=row["week_label"], slots=slots)

    def _load_slots(self, conn: sqlite3.Connection, plan_id: str) -> List[MealSlot]:
        rows = conn.execute(
            "SELECT payload FROM meal_slots WHERE plan_id = ? ORDER BY id",
            (plan_id,),
        ).fetchall()
        slots: List[MealSlot] = []
        for row in rows:
            data = json.loads(row["payload"])
            slots.append(MealSlot(**data))
        return slots

    def save_plan(self, plan: MealPlan, make_active: bool = True) -> MealPlan:
        with self._connect() as conn:
            if make_active:
                conn.execute("UPDATE meal_plans SET is_active = 0")
            conn.execute(
                "INSERT INTO meal_plans (id, week_label, is_active) VALUES (?, ?, ?)",
                (plan.id, plan.week_label, 1 if make_active else 0),
            )
            for slot in plan.slots:
                conn.execute(
                    "INSERT INTO meal_slots (plan_id, day, meal_type, recipe_id, payload) VALUES (?, ?, ?, ?, ?)",
                    (plan.id, slot.day, slot.meal_type, slot.recipe_id, slot.model_dump_json()),
                )
            conn.commit()
        return plan

    def create_empty_plan_id(self) -> str:
        return str(uuid4())
