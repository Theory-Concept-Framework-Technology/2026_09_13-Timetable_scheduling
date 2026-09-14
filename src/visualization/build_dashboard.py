import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import plotly.express as px

from config import (
    OUTPUT_DIR,
    WEB_DIR,
    DAYS,
    PERIODS,
    PERIOD_TIMES,
    DAY_DATES,
    COLOR_BY,
    COLOR_PALETTE,
    FONT_FAMILY,
    BODY_FONT_SIZE,
    TITLE_FONT_SIZE,
    GANTT_HEIGHT,
    PAGE_TITLE,
    SHOW_TEACHER,
    SHOW_ROOM,
    SHOW_SECTION,
    SCHOOL_NAME,
    ACADEMIC_YEAR,
    CURRENT_WEEK_LABEL,
    TIMETABLE_DISPLAY_BREAKS,
)

from .analytics import (
    compute_kpis,
    detect_conflicts,
    room_utilization,
    teacher_workload,
    timetable_records,
)
from .html_templates import (
    build_dashboard_html,
    dataframe_to_html,
    render_about_section,
    render_conflicts,
    render_constraints_panel,
    render_dataset_summary,
    render_empty_state,
    render_kpi_cards,
    render_optimization_summary,
    render_pipeline,
    render_technical_details,
    render_utilization_bars,
    render_workload_bars,
)


OUTPUT_HTML = OUTPUT_DIR / "timetable_gantt.html"


def copy_web_assets() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    for name in ("style.css", "app.js"):
        src = WEB_DIR / name
        if src.is_file():
            shutil.copy2(src, OUTPUT_DIR / name)


def load_optimization_summary() -> Optional[Dict]:
    path = OUTPUT_DIR / "optimization_summary.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def load_csv_safe(path: Path) -> Optional[pd.DataFrame]:
    if not path.is_file():
        return None
    try:
        df = pd.read_csv(path)
        return df
    except (pd.errors.ParserError, OSError, ValueError):
        return None


def write_empty_dashboard(message: str) -> None:
    copy_web_assets()
    OUTPUT_HTML.write_text(
        render_empty_state(message),
        encoding="utf-8",
    )
    print("\n======================================")
    print("DASHBOARD CREATED (EMPTY STATE)")
    print("======================================")
    print("\nHTML:")
    print(OUTPUT_HTML)


def create_color_map(values: pd.Series) -> Dict[str, str]:
    unique_values = sorted(values.dropna().astype(str).unique())
    color_map = {}
    for index, value in enumerate(unique_values):
        color_map[value] = COLOR_PALETTE[index % len(COLOR_PALETTE)]
    return color_map


def build_gantt_html(timetable: pd.DataFrame, color_map: Dict[str, str]) -> str:
    tt = timetable.copy()
    tt["start_time"] = tt["period"].apply(
        lambda p: PERIOD_TIMES[int(p)][0]
    )
    tt["end_time"] = tt["period"].apply(
        lambda p: PERIOD_TIMES[int(p)][1]
    )
    tt["date"] = tt["day"].map(DAY_DATES)
    tt["start"] = pd.to_datetime(
        tt["date"] + " " + tt["start_time"]
    )
    tt["end"] = pd.to_datetime(
        tt["date"] + " " + tt["end_time"]
    )
    tt["time_range"] = (
        tt["start_time"] + " – " + tt["end_time"]
    )

    fig = px.timeline(
        tt,
        x_start="start",
        x_end="end",
        y="room",
        color=COLOR_BY,
        color_discrete_map=color_map,
        text="course_name",
        hover_data={
            "course_name": True,
            "teacher": True,
            "room": True,
            "day": True,
            "time_range": True,
            "section": True,
            "start": False,
            "end": False,
        },
        title="Weekly Timetable — Room Timeline",
    )

    fig.update_yaxes(title="Room", autorange="reversed")
    fig.update_xaxes(
        title="Day / Time",
        tickformat="%a %d %b<br>%H:%M",
    )
    fig.update_traces(
        textposition="inside",
        marker_line_width=1,
    )
    fig.update_layout(
        height=GANTT_HEIGHT,
        font=dict(family=FONT_FAMILY, size=BODY_FONT_SIZE),
        title_font=dict(size=TITLE_FONT_SIZE),
        xaxis=dict(rangeslider=dict(visible=True)),
        legend_title=COLOR_BY.replace("_", " ").title(),
        hoverlabel=dict(namelength=-1),
        margin=dict(l=60, r=40, t=80, b=70),
    )

    return fig.to_html(full_html=False, include_plotlyjs="inline")


def period_times_for_js() -> Dict[str, List[str]]:
    return {
        str(p): [PERIOD_TIMES[p][0], PERIOD_TIMES[p][1]]
        for p in PERIODS
    }


def main() -> None:
    copy_web_assets()

    teachers = load_csv_safe(OUTPUT_DIR / "teachers.csv")
    rooms = load_csv_safe(OUTPUT_DIR / "rooms.csv")
    courses = load_csv_safe(OUTPUT_DIR / "courses.csv")
    timetable = load_csv_safe(OUTPUT_DIR / "timetable.csv")

    missing = []
    if teachers is None:
        missing.append("teachers.csv")
    if rooms is None:
        missing.append("rooms.csv")
    if courses is None:
        missing.append("courses.csv")
    if timetable is None:
        missing.append("timetable.csv")

    if missing:
        write_empty_dashboard(
            "No timetable has been generated yet. Missing: "
            + ", ".join(missing)
        )
        return

    if timetable.empty:
        write_empty_dashboard(
            "Timetable file exists but contains no scheduled classes."
        )
        return

    optimization = load_optimization_summary()
    conflicts = detect_conflicts(timetable, courses)
    kpis = compute_kpis(
        teachers,
        rooms,
        courses,
        timetable,
        DAYS,
        PERIODS,
        optimization,
    )

    num_slots = len(DAYS) * len(PERIODS)
    room_util = room_utilization(timetable, rooms, num_slots)
    workload = teacher_workload(timetable, teachers)

    color_map = create_color_map(timetable[COLOR_BY].astype(str))
    gantt_html = build_gantt_html(timetable, color_map)

    teachers_html = dataframe_to_html(teachers)
    rooms_html = dataframe_to_html(rooms)
    courses_html = dataframe_to_html(courses)
    timetable_html = dataframe_to_html(
        timetable[
            [
                "course_id",
                "course_name",
                "section",
                "teacher",
                "room",
                "day",
                "period",
            ]
        ]
    )

    teacher_name_map = {}
    if not teachers.empty:
        for _, trow in teachers.iterrows():
            teacher_name_map[str(trow["teacher_id"])] = str(
                trow.get("teacher_name", trow["teacher_id"])
            )

    room_capacity_map = {}
    if not rooms.empty:
        for _, rrow in rooms.iterrows():
            room_capacity_map[str(rrow["room_id"])] = rrow.get("capacity")

    tt_records = timetable_records(timetable)
    for rec in tt_records:
        tid = str(rec.get("teacher", ""))
        rec["teacher_name"] = teacher_name_map.get(tid, tid)

    sections = sorted(
        courses["section"].dropna().astype(str).unique().tolist()
    ) if "section" in courses.columns else []

    dashboard_json = {
        "days": DAYS,
        "dayShort": {
            "Monday": "MON",
            "Tuesday": "TUE",
            "Wednesday": "WED",
            "Thursday": "THU",
            "Friday": "FRI",
        },
        "periods": PERIODS,
        "periodTimes": period_times_for_js(),
        "breakRows": TIMETABLE_DISPLAY_BREAKS,
        "colorBy": COLOR_BY,
        "colorMap": color_map,
        "showTeacher": SHOW_TEACHER,
        "showRoom": SHOW_ROOM,
        "showSection": SHOW_SECTION,
        "schoolName": SCHOOL_NAME,
        "academicYear": ACADEMIC_YEAR,
        "weekLabel": CURRENT_WEEK_LABEL,
        "weekOptions": [CURRENT_WEEK_LABEL],
        "sections": sections,
        "classOptions": ["All Classes"],
        "teacherNames": teacher_name_map,
        "roomCapacities": room_capacity_map,
        "roomUtilization": room_util,
        "timetable": tt_records,
        "teachers": timetable_records(teachers),
        "rooms": timetable_records(rooms),
        "courses": timetable_records(courses),
        "kpis": kpis,
    }

    room_util_html = render_utilization_bars(
        room_util,
        "Room Utilization",
        "room_id",
        "utilization_pct",
        subtitle_key="classes_scheduled",
    )

    html = build_dashboard_html(
        page_title=PAGE_TITLE,
        gantt_html=gantt_html,
        teachers_html=teachers_html,
        rooms_html=rooms_html,
        courses_html=courses_html,
        timetable_html=timetable_html,
        kpi_html=render_kpi_cards(kpis),
        optimization_html=render_optimization_summary(
            kpis, len(conflicts)
        ),
        room_util_html=room_util_html,
        workload_html=render_workload_bars(workload),
        conflicts_html=render_conflicts(conflicts),
        pipeline_html=render_pipeline(),
        constraints_html=render_constraints_panel(),
        technical_html=render_technical_details(kpis, optimization),
        about_html=render_about_section(),
        dataset_html=render_dataset_summary(
            teachers, rooms, courses, DAYS, PERIODS, PERIOD_TIMES
        ),
        dashboard_json=dashboard_json,
    )

    OUTPUT_HTML.write_text(html, encoding="utf-8")

    data_path = OUTPUT_DIR / "dashboard-data.json"
    data_path.write_text(
        json.dumps(dashboard_json, indent=2, default=str),
        encoding="utf-8",
    )

    print("\n======================================")
    print("DASHBOARD CREATED SUCCESSFULLY")
    print("======================================")
    print("\nHTML:")
    print(OUTPUT_HTML)


if __name__ == "__main__":
    main()
