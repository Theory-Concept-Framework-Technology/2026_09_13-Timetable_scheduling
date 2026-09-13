
from docplex.mp.model import Model
import pandas as pd
import os


# =====================================================
# 1. LOAD DATA
# =====================================================

courses = pd.read_csv("output/courses.csv")

# Use only 4 rooms to keep the model below
# CPLEX Community Edition's 1000-variable limit.
rooms = pd.read_csv("output/rooms.csv").head(4)

print("Courses loaded:", len(courses))
print("Rooms loaded:", len(rooms))


# =====================================================
# 2. TIMETABLE SETTINGS
# =====================================================

days = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday"
]

# 3 periods per day
periods = [1, 2, 3]


# =====================================================
# 3. CREATE MODEL
# =====================================================

model = Model("College_Timetable")


# =====================================================
# 4. CREATE DECISION VARIABLES
# =====================================================

x = {}

for _, course in courses.iterrows():

    c = course["course_id"]

    for _, room in rooms.iterrows():

        r = room["room_id"]

        for day in days:

            for period in periods:

                x[c, r, day, period] = model.binary_var(
                    name=f"x_{c}_{r}_{day}_{period}"
                )


print("\nDecision variables:", len(x))


# =====================================================
# 5. CHECK CPLEX COMMUNITY EDITION LIMIT
# =====================================================

if len(x) > 1000:

    print("\nERROR:")
    print("The model has more than 1000 variables.")
    print("Current variables:", len(x))
    print("Reduce courses, rooms, or periods.")

    exit()


# =====================================================
# 6. CONSTRAINT 1
# EVERY COURSE MUST BE SCHEDULED
# ACCORDING TO WEEKLY CLASSES
# =====================================================

for _, course in courses.iterrows():

    c = course["course_id"]

    required = int(course["weekly_classes"])

    model.add_constraint(

        model.sum(
            x[c, r, d, p]

            for r in rooms["room_id"]
            for d in days
            for p in periods

        ) == required

    )


# =====================================================
# 7. CONSTRAINT 2
# ONE ROOM CANNOT HAVE TWO CLASSES
# AT THE SAME TIME
# =====================================================

for r in rooms["room_id"]:

    for d in days:

        for p in periods:

            model.add_constraint(

                model.sum(
                    x[c, r, d, p]
                    for c in courses["course_id"]
                ) <= 1

            )


# =====================================================
# 8. CONSTRAINT 3
# ONE SECTION CANNOT HAVE TWO CLASSES
# AT THE SAME TIME
# =====================================================

for section in courses["section"].unique():

    section_courses = courses[
        courses["section"] == section
    ]["course_id"]

    for d in days:

        for p in periods:

            model.add_constraint(

                model.sum(
                    x[c, r, d, p]

                    for c in section_courses
                    for r in rooms["room_id"]

                ) <= 1

            )


# =====================================================
# 9. CONSTRAINT 4
# ONE TEACHER CANNOT TEACH TWO CLASSES
# AT THE SAME TIME
# =====================================================

for teacher in courses["teacher_id"].unique():

    teacher_courses = courses[
        courses["teacher_id"] == teacher
    ]["course_id"]

    for d in days:

        for p in periods:

            model.add_constraint(

                model.sum(
                    x[c, r, d, p]

                    for c in teacher_courses
                    for r in rooms["room_id"]

                ) <= 1

            )


# =====================================================
# 10. OBJECTIVE FUNCTION
# =====================================================

# Try to avoid using Period 3 too much.
# This gives CPLEX something to optimize.

late_period_penalty = model.sum(

    x[c, r, d, 3]

    for c in courses["course_id"]

    for r in rooms["room_id"]

    for d in days

)

model.minimize(late_period_penalty)


# =====================================================
# 11. SOLVE MODEL
# =====================================================

print("\n======================================")
print("Starting CPLEX optimization...")
print("======================================\n")

solution = model.solve(log_output=True)


# =====================================================
# 12. CHECK SOLUTION
# =====================================================

if solution:

    print("\n======================================")
    print("OPTIMAL TIMETABLE FOUND!")
    print("======================================")

    print("\nObjective value:")
    print(solution.objective_value)


    # =================================================
    # 13. EXTRACT TIMETABLE
    # =================================================

    timetable = []

    for _, course in courses.iterrows():

        c = course["course_id"]

        for r in rooms["room_id"]:

            for d in days:

                for p in periods:

                    value = solution.get_value(
                        x[c, r, d, p]
                    )

                    if value > 0.5:

                        timetable.append({

                            "course_id":
                                c,

                            "course_name":
                                course["course_name"],

                            "section":
                                course["section"],

                            "teacher":
                                course["teacher_id"],

                            "room":
                                r,

                            "day":
                                d,

                            "period":
                                p

                        })


    # =================================================
    # 14. CREATE DATAFRAME
    # =================================================

    timetable_df = pd.DataFrame(timetable)


    # =================================================
    # 15. CREATE OUTPUT DIRECTORY
    # =================================================

    os.makedirs(
        "output",
        exist_ok=True
    )


    # =================================================
    # 16. SAVE TIMETABLE
    # =================================================

    output_file = "output/timetable.csv"

    timetable_df.to_csv(
        output_file,
        index=False
    )


    # =================================================
    # 17. DISPLAY RESULT
    # =================================================

    print("\nTimetable saved successfully!")

    print(
        "File:",
        output_file
    )

    print("\nNumber of scheduled classes:")

    print(
        len(timetable_df)
    )

    print("\nGenerated timetable:")

    print(
        timetable_df.to_string(
            index=False
        )
    )


else:

    print("\n======================================")
    print("NO FEASIBLE TIMETABLE FOUND")
    print("======================================")

    print(
        "\nPossible reasons:"
    )

    print(
        "1. Too many weekly classes."
    )

    print(
        "2. Too few rooms."
    )

    print(
        "3. Too few periods."
    )

    print(
        "4. Teacher conflicts."
    )

    print(
        "5. Section conflicts."
    )

