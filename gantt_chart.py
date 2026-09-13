import pandas as pd
import plotly.express as px
import os


# =====================================================
# 1. FILE PATH
# =====================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

input_file = os.path.join(
    BASE_DIR,
    "output",
    "timetable.csv"
)

output_file = os.path.join(
    BASE_DIR,
    "output",
    "timetable_gantt.html"
)


# =====================================================
# 2. CHECK FILE
# =====================================================

if not os.path.exists(input_file):

    print("ERROR: timetable.csv not found.")

    print(
        "\nExpected file:"
    )

    print(input_file)

    print(
        "\nRun model.py first."
    )

    exit()


# =====================================================
# 3. READ TIMETABLE
# =====================================================

df = pd.read_csv(input_file)

print("\nTimetable loaded successfully.")

print("\nColumns:")

print(df.columns.tolist())


# =====================================================
# 4. PERIOD TIME MAPPING
# =====================================================

period_times = {

    1: ("09:00", "10:00"),

    2: ("10:00", "11:00"),

    3: ("11:00", "12:00")
}


df["start_time"] = df["period"].map(
    lambda x: period_times[int(x)][0]
)

df["end_time"] = df["period"].map(
    lambda x: period_times[int(x)][1]
)


# =====================================================
# 5. CREATE A DATE FOR EACH DAY
# =====================================================

day_dates = {

    "Monday": "2026-01-05",

    "Tuesday": "2026-01-06",

    "Wednesday": "2026-01-07",

    "Thursday": "2026-01-08",

    "Friday": "2026-01-09"
}


df["date"] = df["day"].map(day_dates)


# =====================================================
# 6. CREATE DATETIME
# =====================================================

df["start"] = pd.to_datetime(
    df["date"] + " " + df["start_time"]
)

df["end"] = pd.to_datetime(
    df["date"] + " " + df["end_time"]
)


# =====================================================
# 7. DISPLAY LABEL
# =====================================================

df["class_name"] = (

    df["course_name"]

    + " ("

    + df["section"]

    + ")"

)


# =====================================================
# 8. CREATE GANTT CHART
# =====================================================

fig = px.timeline(

    df,

    x_start="start",

    x_end="end",

    y="room",

    color="section",

    text="course_name",

    hover_data=[

        "course_id",

        "course_name",

        "section",

        "teacher",

        "room",

        "day",

        "period"

    ],

    title="College Timetable - CPLEX Generated Schedule"
)


# =====================================================
# 9. FORMAT CHART
# =====================================================

fig.update_yaxes(

    title="Room",

    autorange="reversed"
)


fig.update_xaxes(

    title="Day / Time",

    tickformat="%a %d %b<br>%H:%M"
)


fig.update_traces(

    textposition="inside"
)


fig.update_layout(

    height=700,

    xaxis=dict(

        rangeslider=dict(
            visible=True
        )
    ),

    legend_title="Section",

    hoverlabel=dict(
        namelength=-1
    )
)


# =====================================================
# 10. SAVE HTML
# =====================================================

fig.write_html(
    output_file
)


# =====================================================
# 11. SHOW RESULT
# =====================================================

print("\n======================================")

print("GANTT CHART CREATED SUCCESSFULLY!")

print("======================================")

print("\nHTML file:")

print(output_file)


