"""Compute dashboard KPIs, utilization, workload, and post-hoc conflict checks."""

from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def compute_required_classes(courses: pd.DataFrame) -> int:
    if courses.empty or "weekly_classes" not in courses.columns:
        return 0
    return _safe_int(courses["weekly_classes"].sum())


def compute_kpis(
    teachers: pd.DataFrame,
    rooms: pd.DataFrame,
    courses: pd.DataFrame,
    timetable: pd.DataFrame,
    days: List[str],
    periods: List[int],
    optimization: Optional[Dict],
) -> Dict[str, Any]:
    required = compute_required_classes(courses)
    scheduled = len(timetable)
    unscheduled = max(0, required - scheduled)
    time_slots = len(days) * len(periods)

    obj_val = None
    solver_status = None
    num_vars = None
    num_constraints = None

    if optimization:
        obj_val = optimization.get("objective_value")
        solver_status = optimization.get("solver_status")
        num_vars = optimization.get("num_decision_variables")
        num_constraints = optimization.get("num_constraints")
        if optimization.get("required_weekly_classes") is not None:
            required = _safe_int(optimization["required_weekly_classes"])
            unscheduled = max(0, required - scheduled)

    status_label, status_class = _optimization_status_label(
        solver_status, scheduled, required, unscheduled
    )

    return {
        "total_courses": len(courses),
        "total_teachers": len(teachers),
        "total_rooms": len(rooms),
        "total_time_slots": time_slots,
        "scheduled_classes": scheduled,
        "required_classes": required,
        "unscheduled_classes": unscheduled,
        "objective_value": obj_val,
        "solver_status": solver_status,
        "num_decision_variables": num_vars,
        "num_constraints": num_constraints,
        "optimization_status_label": status_label,
        "optimization_status_class": status_class,
    }


def _optimization_status_label(
    solver_status: Optional[str],
    scheduled: int,
    required: int,
    unscheduled: int,
) -> Tuple[str, str]:
    if solver_status is None:
        if scheduled >= required and required > 0:
            return "Scheduled (solver metadata N/A)", "status-warning"
        if scheduled == 0:
            return "No data", "status-neutral"
        return "Unknown", "status-neutral"

    status_lower = str(solver_status).lower()
    if "optimal" in status_lower or "feasible" in status_lower:
        if unscheduled > 0:
            return "Feasible (incomplete schedule)", "status-warning"
        return "Optimal / Feasible", "status-success"
    if "infeasible" in status_lower:
        return "Infeasible", "status-error"
    return str(solver_status), "status-neutral"


def teacher_workload(
    timetable: pd.DataFrame,
    teachers: pd.DataFrame,
) -> List[Dict[str, Any]]:
    if timetable.empty:
        return []

    counts = (
        timetable.groupby("teacher", dropna=False)
        .size()
        .reset_index(name="class_count")
    )

    name_map = {}
    if not teachers.empty and "teacher_id" in teachers.columns:
        for _, row in teachers.iterrows():
            name_map[str(row["teacher_id"])] = str(
                row.get("teacher_name", row["teacher_id"])
            )

    rows = []
    for _, row in counts.iterrows():
        tid = str(row["teacher"])
        rows.append(
            {
                "teacher_id": tid,
                "teacher_name": name_map.get(tid, tid),
                "class_count": int(row["class_count"]),
            }
        )

    rows.sort(key=lambda r: (-r["class_count"], r["teacher_id"]))
    max_count = max((r["class_count"] for r in rows), default=1)
    for r in rows:
        r["max_count"] = max_count
    return rows


def room_utilization(
    timetable: pd.DataFrame,
    rooms: pd.DataFrame,
    num_day_period_slots: int,
) -> List[Dict[str, Any]]:
    if rooms.empty:
        return []

    scheduled_by_room = {}
    if not timetable.empty and "room" in timetable.columns:
        scheduled_by_room = (
            timetable.groupby("room").size().to_dict()
        )

    rows = []
    for _, room in rooms.iterrows():
        rid = str(room["room_id"])
        scheduled = int(scheduled_by_room.get(rid, 0))
        capacity = room.get("capacity", "—")
        pct = (
            round(100.0 * scheduled / num_day_period_slots, 1)
            if num_day_period_slots > 0
            else 0.0
        )
        rows.append(
            {
                "room_id": rid,
                "capacity": capacity,
                "classes_scheduled": scheduled,
                "utilization_pct": min(100.0, pct),
                "slot_capacity": num_day_period_slots,
            }
        )

    rows.sort(key=lambda r: r["room_id"])
    return rows


def detect_conflicts(
    timetable: pd.DataFrame,
    courses: pd.DataFrame,
) -> List[Dict[str, str]]:
    if timetable.empty:
        return []

    conflicts: List[Dict[str, str]] = []

    def _check_duplicate(
        group_cols: List[str],
        label: str,
        id_col: str,
    ) -> None:
        grouped = timetable.groupby(["day", "period"] + group_cols)
        for keys, group in grouped:
            if len(group) <= 1:
                continue
            day, period = keys[0], keys[1]
            entity = keys[2] if len(keys) > 2 else "?"
            courses_list = ", ".join(
                group["course_name"].astype(str).tolist()
            )
            conflicts.append(
                {
                    "type": label,
                    "day": str(day),
                    "period": str(period),
                    "entity": str(entity),
                    "detail": (
                        f"{label} {entity} has {len(group)} classes "
                        f"on {day} period {period}: {courses_list}"
                    ),
                }
            )

    if "teacher" in timetable.columns:
        _check_duplicate(["teacher"], "Teacher", "teacher")
    if "room" in timetable.columns:
        _check_duplicate(["room"], "Room", "room")

    section_source = timetable
    if "section" not in timetable.columns and not courses.empty:
        section_source = timetable.merge(
            courses[["course_id", "section"]],
            on="course_id",
            how="left",
        )

    if "section" in section_source.columns:
        grouped = section_source.groupby(["day", "period", "section"])
        for (day, period, section), group in grouped:
            if pd.isna(section) or len(group) <= 1:
                continue
            courses_list = ", ".join(
                group["course_name"].astype(str).tolist()
            )
            conflicts.append(
                {
                    "type": "Section",
                    "day": str(day),
                    "period": str(period),
                    "entity": str(section),
                    "detail": (
                        f"Section {section} has {len(group)} classes "
                        f"on {day} period {period}: {courses_list}"
                    ),
                }
            )

    return conflicts


def timetable_records(timetable: pd.DataFrame) -> List[Dict[str, Any]]:
    if timetable.empty:
        return []
    records = timetable.to_dict(orient="records")
    for rec in records:
        for key, val in rec.items():
            if pd.isna(val):
                rec[key] = None
            elif hasattr(val, "item"):
                try:
                    rec[key] = val.item()
                except (ValueError, AttributeError):
                    rec[key] = val
    return records
