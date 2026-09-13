@echo off

setlocal

REM ============================================================
REM PROJECT ROOT
REM ============================================================

cd /d "%~dp0"

echo.
echo ============================================================
echo       SCHOOL TIMETABLE SCHEDULING SYSTEM
echo ============================================================
echo.


REM ============================================================
REM CHECK UV
REM ============================================================

where uv >nul 2>&1

if errorlevel 1 (
    echo ERROR: uv is not installed or not available in PATH.
    echo.
    echo Install uv first.
    pause
    exit /b 1
)


REM ============================================================
REM PYTHON SOURCE
REM ============================================================

set PYTHON_SOURCE=C:\Users\shukl\anaconda3\python.exe

if not exist "%PYTHON_SOURCE%" (
    echo ERROR:
    echo Python source not found:
    echo %PYTHON_SOURCE%
    echo.
    pause
    exit /b 1
)


REM ============================================================
REM VIRTUAL ENVIRONMENT
REM ============================================================

set VENV_PYTHON=.TIMEenvTABLE\Scripts\python.exe

if not exist "%VENV_PYTHON%" (

    echo.
    echo Virtual environment not found.
    echo Creating .TIMEenvTABLE...
    echo.

    uv venv ".TIMEenvTABLE" --python "%PYTHON_SOURCE%"

    if errorlevel 1 (
        echo.
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
)


REM ============================================================
REM INSTALL / UPDATE REQUIREMENTS
REM ============================================================

echo.
echo ============================================================
echo Installing required packages...
echo ============================================================
echo.

uv pip install ^
    --python "%VENV_PYTHON%" ^
    -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Package installation failed.
    pause
    exit /b 1
)


REM ============================================================
REM STEP 1 - DATA GENERATION
REM ============================================================

echo.
echo ============================================================
echo STEP 1/3 - DATA GENERATION
echo ============================================================
echo.

"%VENV_PYTHON%" -m src.data_generation.generate_data

if errorlevel 1 (
    echo.
    echo ERROR: Data generation failed.
    pause
    exit /b 1
)


REM ============================================================
REM STEP 2 - CPLEX MODEL
REM ============================================================

echo.
echo ============================================================
echo STEP 2/3 - CPLEX TIMETABLE OPTIMIZATION
echo ============================================================
echo.

"%VENV_PYTHON%" -m src.model.build_model

if errorlevel 1 (
    echo.
    echo ERROR: CPLEX model failed.
    pause
    exit /b 1
)


REM ============================================================
REM STEP 3 - DASHBOARD
REM ============================================================

echo.
echo ============================================================
echo STEP 3/3 - BUILDING DASHBOARD
echo ============================================================
echo.

"%VENV_PYTHON%" -m src.visualization.build_dashboard

if errorlevel 1 (
    echo.
    echo ERROR: Dashboard generation failed.
    pause
    exit /b 1
)


REM ============================================================
REM FINISHED
REM ============================================================

echo.
echo ============================================================
echo              PROCESS COMPLETED
echo ============================================================
echo.

echo Dashboard:
echo %CD%\output\timetable_gantt.html

echo.

echo Opening dashboard...

start "" "%CD%\output\timetable_gantt.html"

echo.
pause