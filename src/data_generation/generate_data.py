from faker import Faker
import pandas as pd
import random

from config import (
    OUTPUT_DIR,
    RANDOM_SEED,
    NUMBER_OF_TEACHERS,
    NUMBER_OF_ROOMS
)


# ============================================================
# SETUP
# ============================================================

fake = Faker()

random.seed(RANDOM_SEED)
Faker.seed(RANDOM_SEED)

OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================
# TEACHERS
# ============================================================

teachers = []

for i in range(NUMBER_OF_TEACHERS):

    teachers.append({
        "teacher_id": f"T{i + 1}",
        "teacher_name": fake.name()
    })


teachers_df = pd.DataFrame(teachers)


# ============================================================
# ROOMS
# ============================================================

rooms = []

for i in range(NUMBER_OF_ROOMS):

    rooms.append({
        "room_id": f"R{i + 1}",
        "capacity": random.choice([30, 40, 50, 60])
    })


rooms_df = pd.DataFrame(rooms)


# ============================================================
# SUBJECTS
# ============================================================

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


# ============================================================
# COURSES
# ============================================================

courses = []

for i, subject in enumerate(subjects):

    courses.append({

        "course_id": f"C{i + 1}",

        "course_name": subject,

        "teacher_id": random.choice(
            teachers_df["teacher_id"].tolist()
        ),

        "section": random.choice(
            ["A", "B"]
        ),

        "weekly_classes": 1
    })


courses_df = pd.DataFrame(courses)


# ============================================================
# SAVE
# ============================================================

teachers_df.to_csv(
    OUTPUT_DIR / "teachers.csv",
    index=False
)

rooms_df.to_csv(
    OUTPUT_DIR / "rooms.csv",
    index=False
)

courses_df.to_csv(
    OUTPUT_DIR / "courses.csv",
    index=False
)


# ============================================================
# DISPLAY
# ============================================================

print("\n======================================")
print("DATA GENERATION COMPLETE")
print("======================================")

print(f"\nTeachers: {len(teachers_df)}")
print(f"Rooms: {len(rooms_df)}")
print(f"Courses: {len(courses_df)}")

print("\nFiles created:")

print(OUTPUT_DIR / "teachers.csv")
print(OUTPUT_DIR / "rooms.csv")
print(OUTPUT_DIR / "courses.csv")

print(
    "\nTotal weekly classes:",
    courses_df["weekly_classes"].sum()
)