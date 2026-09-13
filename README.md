```
D:\School_Timetable_scheduling
│
├── run.bat
├── config.py
├── requirements.txt
├── .gitignore
│
├── src
│   ├── __init__.py
│   │
│   ├── data_generation
│   │   ├── __init__.py
│   │   └── generate_data.py
│   │
│   ├── model
│   │   ├── __init__.py
│   │   └── build_model.py
│   │
│   └── visualization
│       ├── __init__.py
│       └── build_dashboard.py
│
├── web
│   └── style.css
│
└── output
    ├── teachers.csv
    ├── rooms.csv
    ├── courses.csv
    ├── timetable.csv
    └── timetable_gantt.html

```


```
run.bat
   │
   ├── Check .TIMEenvTABLE
   │
   ├── Create environment if missing
   │
   ├── Install requirements
   │
   ▼
generate_data.py
   │
   ├── teachers.csv
   ├── rooms.csv
   └── courses.csv
          │
          ▼
build_model.py
   │
   └── timetable.csv
          │
          ▼
build_dashboard.py
   │
   ├── Gantt Chart
   ├── Day × Time timetable
   ├── Teachers CSV
   ├── Rooms CSV
   ├── Courses CSV
   └── Timetable CSV
          │
          ▼
output/timetable_gantt.html

```

### Future Approach

```
src/
│
├── data_generation/
│   └── generate_data.py
│
├── model/
│   ├── variables.py
│   ├── constraints.py
│   ├── objective.py
│   └── build_model.py
│
├── visualization/
│   ├── gantt.py
│   ├── timetable_grid.py
│   ├── tables.py
│   └── build_dashboard.py
│
└── utils/
    ├── colors.py
    └── file_utils.py

```

```
variables.py
       ↓
constraints.py
       ↓
objective.py
       ↓
solver
       ↓
timetable.csv
```


#### That will make it much easier when you add things such as:

- teacher availability
- room capacity
- lunch break
- multiple classes per subject
- teacher preference
- room preference
- no consecutive classes
- maximum classes per day
- section-specific schedules
- different working hours
- Saturday/Sunday
- multiple semesters
- optimization priorities