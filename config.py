from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "output"
WEB_DIR = BASE_DIR / "src" / "web"

OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================
# DATA GENERATION
# ============================================================

RANDOM_SEED = 42

NUMBER_OF_TEACHERS = 10
NUMBER_OF_ROOMS = 4


# ============================================================
# TIMETABLE SETTINGS
# ============================================================

DAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday"
]

PERIODS = [1, 2, 3]

PERIOD_TIMES = {
    1: ("09:00", "10:00"),
    2: ("10:00", "11:00"),
    3: ("11:00", "12:00")
}


DAY_DATES = {
    "Monday": "2026-01-05",
    "Tuesday": "2026-01-06",
    "Wednesday": "2026-01-07",
    "Thursday": "2026-01-08",
    "Friday": "2026-01-09"
}


# ============================================================
# VISUALIZATION SETTINGS
# ============================================================

# Available:
# "course_name"
# "teacher"
# "section"

COLOR_BY = "course_name"


# ------------------------------------------------------------
# FONT
# ------------------------------------------------------------

FONT_FAMILY = "Segoe UI"
BODY_FONT_SIZE = 14
TITLE_FONT_SIZE = 26
SUBTITLE_FONT_SIZE = 15
TABLE_FONT_SIZE = 13
CELL_TITLE_SIZE = 14
CELL_DETAIL_SIZE = 11


# ------------------------------------------------------------
# CHART SIZE
# ------------------------------------------------------------

GANTT_HEIGHT = 650
GANTT_BAR_HEIGHT = 0.6


# ------------------------------------------------------------
# UI SETTINGS
# ------------------------------------------------------------

PAGE_TITLE = "Smart Timetable Scheduler"

PROJECT_TITLE = "Smart Timetable Scheduler"

PROJECT_SUBTITLE = (
    "Optimization-based Academic Scheduling"
)

TECH_BADGES = [
    "Python",
    "IBM CPLEX",
    "Linear Programming",
    "Faker",
]

SCHOOL_NAME = "Springfield College of Technology"

ACADEMIC_YEAR = "2026–2027"

CURRENT_WEEK_LABEL = "Week of 5 Jan 2026"

# Display-only rows (not from CPLEX); inserted into the weekly grid UI
TIMETABLE_DISPLAY_BREAKS = [
    {
        "start": "12:00",
        "end": "12:30",
        "label": "Lunch",
        "after_period": 3,
    },
]


# ============================================================
# COLOR PALETTE
# ============================================================

COLOR_PALETTE = [
    "#6366F1",
    "#EC4899",
    "#14B8A6",
    "#F59E0B",
    "#8B5CF6",
    "#EF4444",
    "#06B6D4",
    "#84CC16",
    "#F97316",
    "#3B82F6",
    "#A855F7",
    "#10B981",
    "#E11D48",
    "#0EA5E9",
    "#CA8A04",
    "#7C3AED",
    "#059669",
    "#DC2626",
    "#0284C7",
    "#9333EA"
]


# ============================================================
# GRID SETTINGS
# ============================================================

SHOW_TEACHER = True
SHOW_ROOM = True
SHOW_SECTION = True


# # ============================================================
# # CPLEX SETTINGS
# # ============================================================

MAX_VARIABLES = 1000
MAX_CONSTRAINTS = 1000

LATE_PERIOD_PENALTY = 1