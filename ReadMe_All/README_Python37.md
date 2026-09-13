# Timetable Scheduling Optimization

A timetable scheduling project built using **Python, Linear Programming, IBM CPLEX, and Faker**.

The project generates sample academic data, creates an optimized timetable using mathematical constraints, and produces a visual Gantt chart of the scheduled classes.

---

## 🛠️ Tech Stack

- Python 3.7
- IBM CPLEX
- DOcplex
- Pandas
- Faker
- Plotly
- Linear Programming
- PowerShell

---

## 📋 Python Version Requirement

This project requires:

```text
Python 3.7
```

> **Important:** Python 3.7 is required for this project. Using a different Python version may cause dependency or compatibility issues.

The project includes an automated PowerShell setup script that creates the virtual environment using Python 3.7.

---

# 🚀 Setup

## 1. Clone the repository

```powershell
git clone <YOUR_REPOSITORY_URL>
```

Move into the project directory:

```powershell
cd Timetable_scheduling
```

---

## 2. Check Python 3.7

The setup script uses the Windows Python Launcher to find Python 3.7.

Run:

```powershell
py -3.7 --version
```

Expected output:

```text
Python 3.7.x
```

If Python 3.7 is not installed, install Python 3.7 before continuing.

---

# ⚙️ Automatic Environment Setup

The project contains:

```text
setup_env.ps1
```

This script automatically:

1. Checks whether Python 3.7 is installed
2. Creates a virtual environment using Python 3.7
3. Activates the virtual environment
4. Upgrades pip
5. Installs dependencies from `requirements.txt`
6. Verifies the Python version

Run:

```powershell
.\setup_env.ps1
```

After successful execution, the project will contain:

```text
.venv/
```

The environment will use:

```text
Python 3.7
```

---

## 🔐 If PowerShell Blocks the Script

If you see an execution-policy error such as:

```text
running scripts is disabled on this system
```

run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then run:

```powershell
.\setup_env.ps1
```

This changes the execution policy only for the current PowerShell session.

---

# 📦 Manual Environment Setup

If you don't want to use the automated script, you can create the environment manually.

### Create the environment

```powershell
py -3.7 -m venv .venv
```

### Activate it

```powershell
.\.venv\Scripts\Activate.ps1
```

### Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### Install dependencies

```powershell
pip install -r requirements.txt
```

Verify the Python version:

```powershell
python --version
```

Expected:

```text
Python 3.7.x
```

---

# 📁 Project Structure

```text
Timetable_scheduling/
│
├── data/
│   └── ...
│
├── output/
│   ├── timetable.csv
│   └── timetable_gantt.html
│
├── generate_data.py
├── timetable_model.py
├── gantt_chart.py
│
├── requirements.txt
├── setup_env.ps1
├── .python-version
├── .gitignore
└── README.md
```

---

# 🧪 Generate Sample Data

The project uses **Faker** to generate sample data for:

- Teachers
- Subjects
- Rooms
- Student groups
- Course requirements

Run:

```powershell
python generate_data.py
```

---

# 🧮 Run the Optimization Model

The timetable is generated using:

- Linear Programming
- Decision variables
- Constraints
- IBM CPLEX solver

Run:

```powershell
python timetable_model.py
```

The generated timetable will be saved in:

```text
output/timetable.csv
```

---

# 📊 Generate the Gantt Chart

After generating the timetable, run:

```powershell
python gantt_chart.py
```

This generates:

```text
output/timetable_gantt.html
```

---

# 🌐 View the Gantt Chart

You can start a local HTTP server from the `output` directory:

```powershell
cd output
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/timetable_gantt.html
```

---

# 🧠 Optimization Constraints

The model considers constraints such as:

- A course cannot be scheduled more than once in the same period
- A teacher cannot teach two classes simultaneously
- A room cannot be assigned to multiple classes at the same time
- Room capacity must satisfy class requirements
- Required courses must be scheduled
- Valid teacher-course assignments must be maintained

The objective is to generate a feasible timetable while satisfying the defined constraints.

---

# 📄 Dependencies

Project dependencies are maintained in:

```text
requirements.txt
```

Python itself is **not** specified inside `requirements.txt`.

The Python runtime requirement is handled separately through:

```text
.python-version
```

and:

```text
setup_env.ps1
```

---

# 🔄 Recreating the Environment

If you delete the `.venv` folder or clone the project on another Windows machine, simply run:

```powershell
.\setup_env.ps1
```

The environment will be recreated using **Python 3.7** and the dependencies from:

```text
requirements.txt
```

---

# ⚠️ Compatibility Note

Python 3.7 is an older Python release. Some newer versions of Python packages may no longer support Python 3.7.

Therefore, the project should use dependency versions that are compatible with Python 3.7.

For reproducibility, package versions should be pinned in:

```text
requirements.txt
```

Example:

```text
pandas==1.3.5
numpy==1.21.6
Faker==18.13.0
plotly==5.18.0
docplex==2.25.236
```

Use the versions tested with the project rather than always installing the latest versions.

---

# 👩‍💻 Development

Activate the environment before running project commands:

```powershell
.\.venv\Scripts\Activate.ps1
```

You should see something similar to:

```text
(.venv) PS D:\Timetable_scheduling>
```

Then run the required Python scripts.

---

# 📜 License

This project is intended for educational and portfolio purposes.


# ⚡ Alternative Setup Using UV

[uv](https://docs.astral.sh/uv/) is a fast Python package and environment manager.

If you prefer using UV instead of the provided `setup_env.ps1` script, you can create and manage the Python 3.7 environment using the following commands.

> **Note:** The project requires **Python 3.7**.

---
---

## 1. Install UV

If UV is not already installed, install it using PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart PowerShell after installation if the `uv` command is not immediately available.

Verify the installation:

```powershell
uv --version
```

---

## 2. Create a Python 3.7 Environment

From the project root directory, run:

```powershell
uv venv --python 3.7
```

This creates:

```text
.venv/
```

using Python 3.7.

You can verify the Python version with:

```powershell
.venv\Scripts\python.exe --version
```

Expected:

```text
Python 3.7.x
```

---

## 3. Activate the Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, your terminal should look similar to:

```text
(.venv) PS D:\Timetable_scheduling>
```

Verify:

```powershell
python --version
```

Expected:

```text
Python 3.7.x
```

---

## 4. Install Dependencies Using UV

Install the packages listed in `requirements.txt`:

```powershell
uv pip install -r requirements.txt
```

UV will install the project dependencies into the active `.venv` environment.

---

## 5. Complete UV Setup in One Command Sequence

For a fresh clone, the complete process is:

```powershell
uv venv --python 3.7
```

```powershell
.\.venv\Scripts\Activate.ps1
```

```powershell
uv pip install -r requirements.txt
```

Verify:

```powershell
python --version
```

and:

```powershell
uv pip list
```

---

## 6. Let UV Manage Python 3.7

If Python 3.7 is not already installed on the system, UV can download a compatible Python interpreter.

Run:

```powershell
uv python install 3.7
```

Then create the environment:

```powershell
uv venv --python 3.7
```

Verify:

```powershell
.venv\Scripts\python.exe --version
```

---

## 7. UV vs PowerShell Setup

There are two supported ways to create the project environment.

### Option A — PowerShell Script

Recommended for users who want a simple automated setup:

```powershell
.\setup_env.ps1
```

The script:

```text
Checks Python 3.7
       ↓
Creates .venv
       ↓
Activates .venv
       ↓
Upgrades pip
       ↓
Installs requirements.txt
```

### Option B — UV

Recommended for users who already use UV:

```powershell
uv python install 3.7
uv venv --python 3.7
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

Both methods create the same:

```text
.venv/
```

environment using:

```text
Python 3.7
```

---

## 📌 Important

Do **not** add this to `requirements.txt`:

```text
python==3.7
```

`requirements.txt` is for Python packages.

The Python version is controlled by the environment setup:

```text
Python 3.7
    ↓
uv venv --python 3.7
    ↓
.venv
    ↓
uv pip install -r requirements.txt
```

This keeps the project environment and package dependencies separate.