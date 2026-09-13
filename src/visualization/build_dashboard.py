import html
import pandas as pd
import plotly.express as px

from config import (
    OUTPUT_DIR,
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
    GANTT_BAR_HEIGHT,
    PAGE_TITLE,
    PROJECT_TITLE,
    PROJECT_SUBTITLE,
    SHOW_TEACHER,
    SHOW_ROOM,
    SHOW_SECTION
)


# ============================================================
# LOAD DATA
# ============================================================

teachers = pd.read_csv(
    OUTPUT_DIR / "teachers.csv"
)

rooms = pd.read_csv(
    OUTPUT_DIR / "rooms.csv"
)

courses = pd.read_csv(
    OUTPUT_DIR / "courses.csv"
)

timetable = pd.read_csv(
    OUTPUT_DIR / "timetable.csv"
)


# ============================================================
# COLOR MAP
# ============================================================

def create_color_map(values):

    unique_values = sorted(
        values.dropna().astype(str).unique()
    )

    color_map = {}

    for index, value in enumerate(unique_values):

        color_map[value] = COLOR_PALETTE[
            index % len(COLOR_PALETTE)
        ]

    return color_map


color_values = timetable[COLOR_BY].astype(str)

color_map = create_color_map(
    color_values
)


# ============================================================
# GANTT DATA
# ============================================================

timetable["start_time"] = timetable["period"].apply(
    lambda p: PERIOD_TIMES[int(p)][0]
)

timetable["end_time"] = timetable["period"].apply(
    lambda p: PERIOD_TIMES[int(p)][1]
)


timetable["date"] = timetable["day"].map(
    DAY_DATES
)


timetable["start"] = pd.to_datetime(
    timetable["date"]
    + " "
    + timetable["start_time"]
)


timetable["end"] = pd.to_datetime(
    timetable["date"]
    + " "
    + timetable["end_time"]
)


# ============================================================
# GANTT CHART
# ============================================================

fig = px.timeline(

    timetable,

    x_start="start",

    x_end="end",

    y="room",

    color=COLOR_BY,

    color_discrete_map=color_map,

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

    title="Timetable Gantt Chart"
)


fig.update_yaxes(
    title="Room",
    autorange="reversed"
)


fig.update_xaxes(
    title="Day / Time",
    tickformat="%a %d %b<br>%H:%M"
)


fig.update_traces(
    textposition="inside",
    marker_line_width=1
)


fig.update_layout(

    height=GANTT_HEIGHT,

    font=dict(
        family=FONT_FAMILY,
        size=BODY_FONT_SIZE
    ),

    title_font=dict(
        size=TITLE_FONT_SIZE
    ),

    xaxis=dict(

        rangeslider=dict(
            visible=True
        )
    ),

    legend_title=COLOR_BY,

    hoverlabel=dict(
        namelength=-1
    ),

    margin=dict(
        l=60,
        r=40,
        t=80,
        b=70
    )
)


gantt_html = fig.to_html(
    full_html=False,
    include_plotlyjs="inline"
)


# ============================================================
# TIMETABLE GRID
# ============================================================

def create_grid():

    headers = ""

    for period in PERIODS:

        start, end = PERIOD_TIMES[period]

        headers += f"""
        <th>
            <div class="time-header">
                {start}
            </div>

            <div class="time-subheader">
                {end}
            </div>
        </th>
        """


    rows = ""


    for day in DAYS:

        rows += f"""
        <tr>

            <th class="day-cell">
                {day}
            </th>
        """


        for period in PERIODS:

            classes = timetable[
                (timetable["day"] == day)
                &
                (timetable["period"] == period)
            ]


            cell_html = ""


            for _, row in classes.iterrows():

                entity = str(
                    row[COLOR_BY]
                )

                color = color_map.get(
                    entity,
                    "#6366F1"
                )


                teacher_text = ""

                if SHOW_TEACHER:

                    teacher_text = f"""
                    <div class="class-detail">
                        Teacher: {html.escape(
                            str(row["teacher"])
                        )}
                    </div>
                    """


                room_text = ""

                if SHOW_ROOM:

                    room_text = f"""
                    <div class="class-detail">
                        Room: {html.escape(
                            str(row["room"])
                        )}
                    </div>
                    """


                section_text = ""

                if SHOW_SECTION:

                    section_text = f"""
                    <span class="section-badge">
                        {html.escape(
                            str(row["section"])
                        )}
                    </span>
                    """


                cell_html += f"""

                <div
                    class="class-card"
                    style="border-left-color: {color};
                           background: {color}18;"
                >

                    <div class="class-title">

                        {html.escape(
                            str(row["course_name"])
                        )}

                        {section_text}

                    </div>

                    {teacher_text}

                    {room_text}

                </div>

                """


            if not cell_html:

                cell_html = """
                <div class="empty-cell">
                    Free
                </div>
                """


            rows += f"""
                <td class="schedule-cell">
                    {cell_html}
                </td>
            """


        rows += "</tr>"


    return f"""

    <div class="table-wrapper">

        <table class="timetable-grid">

            <thead>

                <tr>

                    <th class="day-header">
                        Day
                    </th>

                    {headers}

                </tr>

            </thead>

            <tbody>

                {rows}

            </tbody>

        </table>

    </div>

    """


grid_html = create_grid()


# ============================================================
# CSV TABLES
# ============================================================

def dataframe_to_html(df):

    return df.to_html(
        index=False,
        classes="data-table",
        border=0
    )


teachers_html = dataframe_to_html(
    teachers
)

rooms_html = dataframe_to_html(
    rooms
)

courses_html = dataframe_to_html(
    courses
)

timetable_html = dataframe_to_html(
    timetable[
        [
            "course_id",
            "course_name",
            "section",
            "teacher",
            "room",
            "day",
            "period"
        ]
    ]
)


# ============================================================
# DASHBOARD HTML
# ============================================================

dashboard_html = f"""
<!DOCTYPE html>

<html>

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>
        {PAGE_TITLE}
    </title>

    <link
        rel="stylesheet"
        href="../web/style.css"
    >

</head>


<body>


<header class="dashboard-header">

    <div>

        <h1>
            {PROJECT_TITLE}
        </h1>

        <p>
            {PROJECT_SUBTITLE}
        </p>

    </div>


    <div class="summary">

        <div class="summary-card">

            <span>
                Courses
            </span>

            <strong>
                {len(courses)}
            </strong>

        </div>


        <div class="summary-card">

            <span>
                Teachers
            </span>

            <strong>
                {len(teachers)}
            </strong>

        </div>


        <div class="summary-card">

            <span>
                Rooms
            </span>

            <strong>
                {len(rooms)}
            </strong>

        </div>


        <div class="summary-card">

            <span>
                Classes
            </span>

            <strong>
                {len(timetable)}
            </strong>

        </div>

    </div>

</header>


<nav class="tabs">

    <button
        class="tab-button active"
        onclick="openTab(event, 'gantt')"
    >
        Gantt Chart
    </button>


    <button
        class="tab-button"
        onclick="openTab(event, 'grid')"
    >
        Day × Time
    </button>


    <button
        class="tab-button"
        onclick="openTab(event, 'teachers')"
    >
        Teachers
    </button>


    <button
        class="tab-button"
        onclick="openTab(event, 'rooms')"
    >
        Rooms
    </button>


    <button
        class="tab-button"
        onclick="openTab(event, 'courses')"
    >
        Courses
    </button>


    <button
        class="tab-button"
        onclick="openTab(event, 'timetable')"
    >
        Timetable Data
    </button>

</nav>


<main class="dashboard-content">


<section
    id="gantt"
    class="tab-content active"
>

    <div class="section-header">

        <h2>
            Gantt Schedule
        </h2>

        <p>
            Room-wise schedule generated by CPLEX.
        </p>

    </div>

    {gantt_html}

</section>


<section
    id="grid"
    class="tab-content"
>

    <div class="section-header">

        <h2>
            Day × Time Timetable
        </h2>

        <p>
            Daily classroom schedule with
            subject, teacher and room details.
        </p>

    </div>

    {grid_html}

</section>


<section
    id="teachers"
    class="tab-content"
>

    <div class="section-header">

        <h2>
            Teachers
        </h2>

        <p>
            Faker generated teacher data.
        </p>

    </div>

    {teachers_html}

</section>


<section
    id="rooms"
    class="tab-content"
>

    <div class="section-header">

        <h2>
            Rooms
        </h2>

        <p>
            Generated classroom information.
        </p>

    </div>

    {rooms_html}

</section>


<section
    id="courses"
    class="tab-content"
>

    <div class="section-header">

        <h2>
            Courses
        </h2>

        <p>
            Generated course information.
        </p>

    </div>

    {courses_html}

</section>


<section
    id="timetable"
    class="tab-content"
>

    <div class="section-header">

        <h2>
            Generated Timetable
        </h2>

        <p>
            Final CPLEX solution.
        </p>

    </div>

    {timetable_html}

</section>


</main>


<script>

function openTab(event, tabName) {{

    const contents =
        document.querySelectorAll(
            ".tab-content"
        );

    contents.forEach(
        function(content) {{
            content.classList.remove("active");
        }}
    );


    const buttons =
        document.querySelectorAll(
            ".tab-button"
        );

    buttons.forEach(
        function(button) {{
            button.classList.remove("active");
        }}
    );


    document
        .getElementById(tabName)
        .classList.add("active");


    event.currentTarget
        .classList.add("active");
}}

</script>


</body>

</html>
"""


# ============================================================
# SAVE
# ============================================================

output_file = (
    OUTPUT_DIR / "timetable_gantt.html"
)

output_file.write_text(
    dashboard_html,
    encoding="utf-8"
)


print("\n======================================")
print("DASHBOARD CREATED SUCCESSFULLY")
print("======================================")

print("\nHTML:")
print(output_file)