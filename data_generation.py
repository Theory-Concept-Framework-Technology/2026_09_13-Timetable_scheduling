from faker import Faker
import pandas as pd
import random
import os


# =====================================================
# 1. SETUP
# =====================================================

fake = Faker()

# Same data every time we run the program
random.seed(42)
Faker.seed(42)

# Make sure output folder exists
os.makedirs("output", exist_ok=True)


# =====================================================
# 2. GENERATE TEACHERS
# =====================================================

teachers = []

for i in range(10):

    teachers.append({
        "teacher_id": f"T{i+1}",
        "teacher_name": fake.name()
    })


teachers_df = pd.DataFrame(teachers)


# =====================================================
# 3. GENERATE ROOMS
# =====================================================

rooms = []

for i in range(4):

    rooms.append({
        "room_id": f"R{i+1}",
        "capacity": random.choice([30, 40, 50, 60])
    })


rooms_df = pd.DataFrame(rooms)


# =====================================================
# 4. SUBJECTS
# =====================================================

subjects = [
    "Python",
    "SQL",
    "Data Structures",
    "DBMS",
    "Machine Learning",
    "Statistics",
    "Computer Networks",
    "Operating Systems",
    "Cloud Computing",
    "Power BI",
    "Artificial Intelligence",
    "Web Development",
    "Data Mining",
    "Cyber Security",
    "Software Engineering"
]


# =====================================================
# 5. CREATE COURSES
# =====================================================

courses = []


# We deliberately control the weekly classes
# so that the CPLEX timetable remains feasible.

weekly_classes_list = [
    1, 1, 1, 1, 1,
    1, 1, 1, 1, 1,
    1, 1, 1, 1, 1
]


for i, subject in enumerate(subjects):

    courses.append({

        "course_id": f"C{i+1}",

        "course_name": subject,

        "teacher_id": random.choice(
            teachers_df["teacher_id"].tolist()
        ),

        "section": random.choice(
            ["A", "B"]
        ),

        "weekly_classes":
            weekly_classes_list[i]
    })


courses_df = pd.DataFrame(courses)


# =====================================================
# 6. SAVE DATA
# =====================================================

teachers_df.to_csv(
    "output/teachers.csv",
    index=False
)

rooms_df.to_csv(
    "output/rooms.csv",
    index=False
)

courses_df.to_csv(
    "output/courses.csv",
    index=False
)


# =====================================================
# 7. DISPLAY GENERATED DATA
# =====================================================

print("\n======================================")
print("TEACHERS")
print("======================================")

print(teachers_df)


print("\n======================================")
print("ROOMS")
print("======================================")

print(rooms_df)


print("\n======================================")
print("COURSES")
print("======================================")

print(courses_df)


print("\n======================================")
print("DATA GENERATION COMPLETE")
print("======================================")

print("\nFiles created:")

print("output/teachers.csv")
print("output/rooms.csv")
print("output/courses.csv")

print("\nTotal weekly classes:",
      courses_df["weekly_classes"].sum())