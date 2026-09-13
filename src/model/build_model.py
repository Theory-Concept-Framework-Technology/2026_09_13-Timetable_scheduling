from docplex.mp.model import Model
import pandas as pd

from config import (
    OUTPUT_DIR,
    DAYS,
    PERIODS,
    MAX_VARIABLES,
    MAX_CONSTRAINTS
)


# ============================================================
# LOAD DATA
# ============================================================

courses = pd.read_csv(
    OUTPUT_DIR / "courses.csv"
)

rooms = pd.read_csv(
    OUTPUT_DIR / "rooms.csv"
)


print("Courses loaded:", len(courses))
print("Rooms loaded:", len(rooms))


# ============================================================
# CREATE MODEL
# ============================================================

model = Model(
    name="College_Timetable"
)


# ============================================================
# DECISION VARIABLES
# ============================================================

x = {}


for _, course in courses.iterrows():

    c = course["course_id"]

    for _, room in rooms.iterrows():

        r = room["room_id"]

        for day in DAYS:

            for period in PERIODS:

                x[c, r, day, period] = model.binary_var(
                    name=f"x_{c}_{r}_{day}_{period}"
                )


print(
    "\nDecision variables:",
    len(x)
)


# ============================================================
# SIZE CHECK
# ============================================================

if len(x) > MAX_VARIABLES:

    raise RuntimeError(
        f"Model contains {len(x)} variables. "
        f"Configured maximum is {MAX_VARIABLES}."
    )


# ============================================================
# CONSTRAINT 1
# COURSE MUST BE SCHEDULED
# ============================================================

for _, course in courses.iterrows():

    c = course["course_id"]

    required = int(
        course["weekly_classes"]
    )

    model.add_constraint(

        model.sum(
            x[c, r, day, period]

            for r in rooms["room_id"]

            for day in DAYS

            for period in PERIODS
        )

        == required
    )


# ============================================================
# CONSTRAINT 2
# ONE ROOM = ONE CLASS
# ============================================================

for room in rooms["room_id"]:

    for day in DAYS:

        for period in PERIODS:

            model.add_constraint(

                model.sum(

                    x[c, room, day, period]

                    for c in courses["course_id"]
                )

                <= 1
            )


# ============================================================
# CONSTRAINT 3
# SECTION CONFLICT
# ============================================================

for section in courses["section"].unique():

    section_courses = courses[
        courses["section"] == section
    ]["course_id"]

    for day in DAYS:

        for period in PERIODS:

            model.add_constraint(

                model.sum(

                    x[c, room, day, period]

                    for c in section_courses

                    for room in rooms["room_id"]
                )

                <= 1
            )


# ============================================================
# CONSTRAINT 4
# TEACHER CONFLICT
# ============================================================

for teacher in courses["teacher_id"].unique():

    teacher_courses = courses[
        courses["teacher_id"] == teacher
    ]["course_id"]

    for day in DAYS:

        for period in PERIODS:

            model.add_constraint(

                model.sum(

                    x[c, room, day, period]

                    for c in teacher_courses

                    for room in rooms["room_id"]
                )

                <= 1
            )


# ============================================================
# CHECK CONSTRAINT COUNT
# ============================================================

print(
    "Constraints:",
    model.number_of_constraints
)

if model.number_of_constraints > MAX_CONSTRAINTS:

    raise RuntimeError(
        "Model exceeds configured CPLEX constraint limit."
    )


# ============================================================
# OBJECTIVE
# ============================================================

late_period_penalty = model.sum(

    x[c, room, day, 3]

    for c in courses["course_id"]

    for room in rooms["room_id"]

    for day in DAYS
)


model.minimize(
    late_period_penalty
)


# ============================================================
# SOLVE
# ============================================================

print("\n======================================")
print("Starting CPLEX optimization...")
print("======================================\n")


solution = model.solve(
    log_output=True
)


# ============================================================
# CHECK
# ============================================================

if not solution:

    raise RuntimeError(
        "NO FEASIBLE TIMETABLE FOUND"
    )


print("\n======================================")
print("OPTIMAL TIMETABLE FOUND!")
print("======================================")

print(
    "\nObjective:",
    solution.objective_value
)


# ============================================================
# EXTRACT RESULT
# ============================================================

timetable = []


for _, course in courses.iterrows():

    c = course["course_id"]

    for room in rooms["room_id"]:

        for day in DAYS:

            for period in PERIODS:

                value = solution.get_value(
                    x[c, room, day, period]
                )

                if value > 0.5:

                    timetable.append({

                        "course_id": c,

                        "course_name":
                            course["course_name"],

                        "section":
                            course["section"],

                        "teacher":
                            course["teacher_id"],

                        "room":
                            room,

                        "day":
                            day,

                        "period":
                            period
                    })


# ============================================================
# SAVE
# ============================================================

timetable_df = pd.DataFrame(
    timetable
)

output_file = (
    OUTPUT_DIR / "timetable.csv"
)

timetable_df.to_csv(
    output_file,
    index=False
)


print("\nTimetable saved:")
print(output_file)

print(
    "\nScheduled classes:",
    len(timetable_df)
)

print(
    "\nGenerated timetable:\n"
)

print(
    timetable_df.to_string(
        index=False
    )
)