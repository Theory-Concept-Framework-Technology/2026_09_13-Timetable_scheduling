# ⚡ Alternative Setup Using UV

[uv](https://docs.astral.sh/uv/) is a fast Python package and environment manager.

If you prefer using UV instead of the provided `setup_env.ps1` script, you can create and manage the Python 3.7 environment using the following commands.

> **Note:** The project requires **Python 3.7**.

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
uv python list
uv venv .TIMEenvTABLE --python cpython-3.7.9-windows-x86_64-none
uv venv .TIMEenvTABLE --python "C:\Users\shukl\anaconda3\python.exe"
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