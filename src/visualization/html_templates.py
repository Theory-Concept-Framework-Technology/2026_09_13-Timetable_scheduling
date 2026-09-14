"""HTML fragment builders for the static dashboard."""

import html
import json
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from config import (
    ACADEMIC_YEAR,
    PROJECT_TITLE,
    SCHOOL_NAME,
)


def escape_text(value: Any) -> str:
    return html.escape(str(value))


def dataframe_to_html(df: pd.DataFrame) -> str:
    if df.empty:
        return '<p class="muted">No data available.</p>'
    return df.to_html(
        index=False,
        classes="data-table",
        border=0,
        escape=True,
    )


def render_empty_state(message: str) -> str:
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Timetable Scheduler</title>
    <link rel="stylesheet" href="style.css">
</head>
<body class="empty-state-body">
    <main class="empty-state-card">
        <h1>{escape_text(PROJECT_TITLE)}</h1>
        <p class="empty-message">{escape_text(message)}</p>
        <ol class="empty-steps">
            <li>Run <code>run.bat</code> from the project root, or</li>
            <li>
                <code>python -m src.data_generation.generate_data</code><br>
                <code>python -m src.model.build_model</code><br>
                <code>python -m src.visualization.build_dashboard</code>
            </li>
        </ol>
        <p class="muted">Then open <code>output/timetable_gantt.html</code>.</p>
    </main>
</body>
</html>
"""


def render_kpi_cards(kpis: Dict[str, Any]) -> str:
    def card(label: str, value: Any) -> str:
        display = escape_text(value) if value is not None else "N/A"
        return f"""
        <div class="kpi-card">
            <span class="kpi-label">{escape_text(label)}</span>
            <strong class="kpi-value">{display}</strong>
        </div>
        """

    obj = kpis.get("objective_value")
    obj_display = (
        f"{obj:.4g}" if isinstance(obj, (int, float)) else "N/A"
    )

    return f"""
    <div class="kpi-grid">
        {card("Total Courses", kpis.get("total_courses"))}
        {card("Teachers", kpis.get("total_teachers"))}
        {card("Rooms", kpis.get("total_rooms"))}
        {card("Time Slots", kpis.get("total_time_slots"))}
        {card("Scheduled Classes", kpis.get("scheduled_classes"))}
        {card("Unscheduled", kpis.get("unscheduled_classes"))}
        {card("Optimization", kpis.get("optimization_status_label"))}
        {card("Objective Value", obj_display)}
    </div>
    """


def render_optimization_summary(
    kpis: Dict[str, Any],
    conflict_count: int,
) -> str:
    status_class = kpis.get("optimization_status_class", "status-neutral")
    status_label = kpis.get("optimization_status_label", "N/A")
    scheduled = kpis.get("scheduled_classes", 0)
    required = kpis.get("required_classes", 0)
    obj = kpis.get("objective_value")
    obj_display = (
        f"{obj:.4g}" if isinstance(obj, (int, float)) else "N/A"
    )
    num_vars = kpis.get("num_decision_variables")
    num_cons = kpis.get("num_constraints")

    return f"""
    <div class="panel optimization-panel">
        <h3>Optimization Summary</h3>
        <div class="opt-grid">
            <div class="opt-item">
                <span class="opt-label">Solver Status</span>
                <span class="status-pill {status_class}">
                    <span class="status-dot"></span>
                    {escape_text(status_label)}
                </span>
            </div>
            <div class="opt-item">
                <span class="opt-label">Objective Value</span>
                <strong>{escape_text(obj_display)}</strong>
            </div>
            <div class="opt-item">
                <span class="opt-label">Decision Variables</span>
                <strong>{escape_text(num_vars if num_vars is not None else "N/A")}</strong>
            </div>
            <div class="opt-item">
                <span class="opt-label">Constraints</span>
                <strong>{escape_text(num_cons if num_cons is not None else "N/A")}</strong>
            </div>
            <div class="opt-item">
                <span class="opt-label">Scheduled Classes</span>
                <strong>{scheduled} / {required}</strong>
            </div>
            <div class="opt-item">
                <span class="opt-label">Conflicts Detected</span>
                <strong>{conflict_count}</strong>
            </div>
        </div>
    </div>
    """


def render_utilization_bars(
    room_rows: List[Dict[str, Any]],
    title: str,
    id_key: str,
    pct_key: str,
    subtitle_key: Optional[str] = None,
) -> str:
    if not room_rows:
        return f'<p class="muted">No {escape_text(title.lower())} data.</p>'

    bars = ""
    for row in room_rows:
        label = row.get(id_key, "")
        pct = float(row.get(pct_key, 0))
        sub = ""
        if subtitle_key and subtitle_key in row:
            val = row[subtitle_key]
            if subtitle_key == "classes_scheduled":
                sub = (
                    f'<span class="bar-sub">{escape_text(val)} classes scheduled</span>'
                )
            else:
                sub = f'<span class="bar-sub">{escape_text(val)}</span>'
        bars += f"""
        <div class="bar-row">
            <div class="bar-label">
                <span>{escape_text(label)}</span>
                {sub}
            </div>
            <div class="bar-track">
                <div class="bar-fill" style="width: {min(100, pct)}%;"></div>
            </div>
            <span class="bar-pct">{pct:.0f}%</span>
        </div>
        """

    return f"""
    <div class="panel">
        <h3>{escape_text(title)}</h3>
        {bars}
    </div>
    """


def render_workload_bars(workload: List[Dict[str, Any]]) -> str:
    if not workload:
        return '<p class="muted">No teacher workload data.</p>'

    max_count = max(r.get("max_count", 1) for r in workload) or 1
    bars = ""
    for row in workload:
        count = int(row.get("class_count", 0))
        pct = round(100.0 * count / max_count, 1)
        name = row.get("teacher_name", row.get("teacher_id", ""))
        tid = row.get("teacher_id", "")
        bars += f"""
        <div class="bar-row">
            <div class="bar-label">
                <span>{escape_text(name)}</span>
                <span class="bar-sub">{escape_text(tid)}</span>
            </div>
            <div class="bar-track">
                <div class="bar-fill bar-fill-alt" style="width: {pct}%;"></div>
            </div>
            <span class="bar-pct">{count}</span>
        </div>
        """

    return f"""
    <div class="panel">
        <h3>Teacher Workload</h3>
        {bars}
    </div>
    """


def render_conflicts(conflicts: List[Dict[str, str]]) -> str:
    if not conflicts:
        return """
        <div class="panel conflict-panel conflict-ok">
            <h3>Scheduling Conflicts</h3>
            <p class="conflict-success">✓ No scheduling conflicts detected in the timetable output.</p>
        </div>
        """

    items = "".join(
        f'<li class="conflict-item">{escape_text(c.get("detail", ""))}</li>'
        for c in conflicts
    )
    return f"""
    <div class="panel conflict-panel conflict-bad">
        <h3>Scheduling Conflicts</h3>
        <ul class="conflict-list">{items}</ul>
    </div>
    """


def render_pipeline() -> str:
    return """
    <div class="panel pipeline-panel">
        <h3>Optimization Pipeline</h3>
        <div class="pipeline">
            <div class="pipeline-step">DATA</div>
            <div class="pipeline-arrow">↓</div>
            <div class="pipeline-step">Faker Generated Data</div>
            <div class="pipeline-arrow">↓</div>
            <div class="pipeline-step">Optimization Model</div>
            <div class="pipeline-arrow">↓</div>
            <div class="pipeline-step">Constraints</div>
            <div class="pipeline-arrow">↓</div>
            <div class="pipeline-step">IBM CPLEX</div>
            <div class="pipeline-arrow">↓</div>
            <div class="pipeline-step">Optimized Timetable</div>
        </div>
    </div>
    """


def render_constraints_panel() -> str:
    rules = [
        (
            "Course coverage",
            "Each course is scheduled exactly as many times per week as its "
            "weekly_classes requirement.",
        ),
        (
            "Room exclusivity",
            "At most one class may use a given room in the same day and period.",
        ),
        (
            "Section exclusivity",
            "At most one class per student section in the same day and period.",
        ),
        (
            "Teacher exclusivity",
            "A teacher cannot teach more than one class in the same day and period.",
        ),
        (
            "Late-period objective",
            "The solver minimizes assignments in the last period of the day "
            "(period 3) when multiple feasible schedules exist.",
        ),
    ]
    items = "".join(
        f"""
        <div class="constraint-card">
            <div class="constraint-title">✓ {escape_text(title)}</div>
            <p class="constraint-purpose">{escape_text(purpose)}</p>
        </div>
        """
        for title, purpose in rules
    )
    note = """
    <p class="muted constraint-note">
        Room capacity values appear in the dataset for reference but are
        <strong>not</strong> enforced in the optimization model.
    </p>
    """
    return f"""
    <div class="panel">
        <h3>Scheduling Rules</h3>
        {items}
        {note}
    </div>
    """


def render_technical_details(
    kpis: Dict[str, Any], optimization: Optional[Dict]
) -> str:
    gen_at = optimization.get("generated_at") if optimization else None
    return f"""
    <details class="panel technical-details">
        <summary>Technical Details</summary>
        <dl class="tech-dl">
            <dt>Optimization Engine</dt>
            <dd>IBM CPLEX</dd>
            <dt>Model</dt>
            <dd>Mixed Integer Programming (binary decision variables)</dd>
            <dt>Python Library</dt>
            <dd>DOcplex</dd>
            <dt>Data Generation</dt>
            <dd>Faker</dd>
            <dt>Decision Variables</dt>
            <dd>{escape_text(kpis.get("num_decision_variables") or "N/A")}</dd>
            <dt>Constraints</dt>
            <dd>{escape_text(kpis.get("num_constraints") or "N/A")}</dd>
            <dt>Last Solve</dt>
            <dd>{escape_text(gen_at or "N/A")}</dd>
        </dl>
    </details>
    """


def render_about_section() -> str:
    return """
    <div class="panel about-panel">
        <h3>About This Project</h3>
        <p>
            Smart Timetable Scheduler generates an optimized college timetable using
            linear programming. Sample academic data is created with Faker, scheduling
            rules are encoded as constraints, and IBM CPLEX searches for a feasible
            solution.
        </p>
        <p class="muted">
            See README.md in the project root for setup and architecture.
        </p>
    </div>
    """


def render_dataset_summary(
    teachers: pd.DataFrame,
    rooms: pd.DataFrame,
    courses: pd.DataFrame,
    days: List[str],
    periods: List[int],
    period_times: Dict[int, Tuple[str, str]],
) -> str:
    period_lines = "<br>".join(
        f"Period {p}: {period_times[p][0]} – {period_times[p][1]}"
        for p in periods
    )
    return f"""
    <div class="panel">
        <h3>Dataset</h3>
        <ul class="dataset-stats">
            <li>Teachers: <strong>{len(teachers)}</strong></li>
            <li>Courses: <strong>{len(courses)}</strong></li>
            <li>Rooms: <strong>{len(rooms)}</strong></li>
            <li>Days: <strong>{len(days)}</strong> ({", ".join(days)})</li>
            <li>Periods per day: <strong>{len(periods)}</strong></li>
        </ul>
        <p class="muted period-list">{period_lines}</p>
    </div>
    """


def build_dashboard_html(
    page_title: str,
    gantt_html: str,
    teachers_html: str,
    rooms_html: str,
    courses_html: str,
    timetable_html: str,
    kpi_html: str,
    optimization_html: str,
    room_util_html: str,
    workload_html: str,
    conflicts_html: str,
    constraints_html: str,
    technical_html: str,
    about_html: str,
    dataset_html: str,
    pipeline_html: str,
    dashboard_json: Dict[str, Any],
) -> str:
    json_script = json.dumps(dashboard_json, default=str)
    json_script = json_script.replace("</", "<\\/")

    school = escape_text(dashboard_json.get("schoolName", SCHOOL_NAME))
    year = escape_text(dashboard_json.get("academicYear", ACADEMIC_YEAR))

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape_text(page_title)}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body class="app-body">
<header class="site-header no-print">
    <div class="site-brand">
        <span class="site-title">{escape_text(PROJECT_TITLE)}</span>
    </div>
    <nav class="top-nav" aria-label="Main">
        <button type="button" class="top-nav-link active" data-section="timetable">Timetable</button>
        <button type="button" class="top-nav-link" data-section="analytics">Analytics</button>
        <button type="button" class="top-nav-link" data-section="optimization">Optimization</button>
        <button type="button" class="top-nav-link" data-section="teachers">Teachers</button>
        <button type="button" class="top-nav-link" data-section="rooms">Rooms</button>
        <button type="button" class="top-nav-link" data-section="gantt">Gantt</button>
        <button type="button" class="top-nav-link" data-section="about">About</button>
    </nav>
</header>

<main class="site-main">
    <!-- PAGE 1: TIMETABLE (default) -->
    <section id="section-timetable" class="page-section active">
        <div class="print-header">
            <h1 class="school-sheet-title">{escape_text(PROJECT_TITLE)}</h1>
            <p class="school-sheet-sub">{school}</p>
            <p class="school-sheet-sub">Academic Year: {year}</p>
        </div>

        <div class="timetable-toolbar no-print">
            <div class="toolbar-filters">
                <label>Class
                    <select id="filter-class"><option value="">All Classes</option></select>
                </label>
                <label>Section
                    <select id="filter-section"><option value="">All Sections</option></select>
                </label>
                <label>Teacher
                    <select id="filter-teacher"><option value="">All Teachers</option></select>
                </label>
                <label>Room
                    <select id="filter-room"><option value="">All Rooms</option></select>
                </label>
                <label>Day
                    <select id="filter-day"><option value="">All Days</option></select>
                </label>
                <label class="mobile-only">Day view
                    <select id="filter-mobile-day"></select>
                </label>
                <label>Week
                    <select id="filter-week"></select>
                </label>
            </div>
            <div class="toolbar-actions">
                <button type="button" class="btn-text" id="btn-print">Print</button>
                <a class="btn-text" href="timetable.csv" download>Download CSV</a>
            </div>
        </div>

        <h2 class="weekly-title">Weekly Timetable</h2>
        <div id="school-timetable-container" class="school-timetable-wrap print-area"></div>
    </section>

    <!-- PAGE 2: ANALYTICS -->
    <section id="section-analytics" class="page-section">
        <h2>Analytics &amp; Insights</h2>
        <p class="muted section-lead">Administrator view — optimization metrics and resource usage.</p>
        {kpi_html}
        <div class="dashboard-grid-2">
            {optimization_html}
            {conflicts_html}
        </div>
        <div class="dashboard-grid-2">
            {room_util_html}
            {workload_html}
        </div>
        {dataset_html}
    </section>

    <!-- PAGE 3: OPTIMIZATION -->
    <section id="section-optimization" class="page-section">
        <h2>Optimization</h2>
        {pipeline_html}
        {optimization_html}
        {constraints_html}
        {technical_html}
        <h3 class="subsection-title">Generated Timetable (raw)</h3>
        {timetable_html}
    </section>

    <!-- PAGE 4: TEACHERS -->
    <section id="section-teachers" class="page-section">
        <h2>Teacher Schedule</h2>
        <div class="entity-toolbar no-print">
            <label>Teacher
                <select id="teacher-page-select"></select>
            </label>
        </div>
        <div id="teacher-timetable-container" class="school-timetable-wrap"></div>
        <h3 class="subsection-title">Teacher registry</h3>
        {teachers_html}
    </section>

    <!-- PAGE 5: ROOMS -->
    <section id="section-rooms" class="page-section">
        <h2>Room Schedule</h2>
        <div class="entity-toolbar no-print">
            <label>Room
                <select id="room-page-select"></select>
            </label>
        </div>
        <div id="room-stats-panel" class="panel room-stats-panel"></div>
        <div id="room-timetable-container" class="school-timetable-wrap"></div>
        <h3 class="subsection-title">Room registry</h3>
        {rooms_html}
    </section>

    <!-- PAGE 6: GANTT -->
    <section id="section-gantt" class="page-section">
        <h2>Gantt View</h2>
        <p class="muted section-lead">Room timeline for technical review.</p>
        <div class="gantt-wrapper panel">{gantt_html}</div>
    </section>

    <!-- ABOUT -->
    <section id="section-about" class="page-section">
        <h2>About</h2>
        {about_html}
    </section>
</main>

<div id="cell-modal" class="cell-modal no-print" hidden>
    <div class="cell-modal-backdrop" id="modal-backdrop"></div>
    <div class="cell-modal-card" role="dialog" aria-modal="true">
        <button type="button" class="cell-modal-close" id="modal-close" aria-label="Close">×</button>
        <div id="modal-content"></div>
    </div>
</div>

<div id="cell-tooltip" class="cell-tooltip no-print" hidden></div>

<script id="dashboard-data" type="application/json">{json_script}</script>
<script src="app.js"></script>
</body>
</html>
"""
