@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Mouse Gaze
set "ROOT=%~dp0"
set "VENV_PY=%ROOT%.venv\Scripts\python.exe"
set "MOUSE_GAZE_VERSION=v2"
if /I "%~1"=="v1" set "MOUSE_GAZE_VERSION=v1"

echo.
echo Mouse Gaze
echo ----------

call :find_python
if errorlevel 1 goto :fail

call :ensure_venv
if errorlevel 1 goto :fail

call :ensure_deps
if errorlevel 1 goto :fail

echo.
echo [4/4] Launching Mouse Gaze (%MOUSE_GAZE_VERSION%)
echo Close the window or press Esc to quit.
echo Version 1, the original drawing: run.bat v1
echo.
"%VENV_PY%" main.py
if errorlevel 1 goto :fail
exit /b 0

:find_python
echo [1/4] Checking Python
where python >nul 2>&1
if not errorlevel 1 (
    python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON=python"
        echo       Python: ready
        exit /b 0
    )
)
where py >nul 2>&1
if not errorlevel 1 (
    py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON=py -3"
        echo       Python: ready
        exit /b 0
    )
)
echo       Python 3.10 or newer was not found on PATH.
echo       Install it from https://www.python.org/downloads/ and try again.
exit /b 1

:ensure_venv
echo [2/4] Checking virtual environment
if exist "%VENV_PY%" (
    "%VENV_PY%" -c "import sys" >nul 2>&1
    if not errorlevel 1 (
        echo       Virtual environment: ready
        exit /b 0
    )
    echo       Virtual environment is unusable. Recreating .venv
    rmdir /s /q "%ROOT%.venv"
)
echo       Creating .venv
%PYTHON% -m venv "%ROOT%.venv"
if errorlevel 1 (
    echo       Could not create the virtual environment.
    exit /b 1
)
if not exist "%VENV_PY%" (
    echo       The virtual environment was not created.
    exit /b 1
)
echo       Virtual environment: created
exit /b 0

:ensure_deps
echo [3/4] Checking dependencies
"%VENV_PY%" -c "import pygame" >nul 2>&1
if not errorlevel 1 (
    echo       Dependencies: ready
    exit /b 0
)
echo       Installing packages from requirements.txt
"%VENV_PY%" -m pip install --upgrade pip
if errorlevel 1 (
    echo       Could not update pip.
    exit /b 1
)
"%VENV_PY%" -m pip install -r "%ROOT%requirements.txt"
if errorlevel 1 (
    echo       Could not install dependencies.
    exit /b 1
)
echo       Dependencies: installed
exit /b 0

:fail
echo.
echo Launch stopped.
pause
exit /b 1
