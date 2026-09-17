@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not on PATH.
    pause
    exit /b 1
)

set MEAL_API_PORT=8000
set LOCAL_WEB_PORT=8080
if exist .env (
    for /f "usebackq tokens=1,* delims==" %%a in (`findstr /b /i "LOCAL_WEB_PORT=" .env`) do set LOCAL_WEB_PORT=%%b
)
if not exist .env copy .env.example .env
if not exist data mkdir data

echo Starting API on http://127.0.0.1:8000 ...
start "Home Meal API" cmd /k "%~dp0run_api.bat"

echo Waiting for API to start...
set /a tries=0
:wait_api
timeout /t 2 /nobreak >nul
powershell -NoProfile -Command "try { (Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/meals/health' -UseBasicParsing -TimeoutSec 2).StatusCode | Out-Null; exit 0 } catch { exit 1 }"
if errorlevel 1 (
    set /a tries+=1
    if !tries! LSS 15 goto wait_api
    echo [WARN] API did not respond yet. Open http://localhost:%LOCAL_WEB_PORT%/ and refresh after the API window is ready.
) else (
    echo API is ready.
)

echo Starting web UI on http://localhost:%LOCAL_WEB_PORT% ...
echo ^(Frontend talks to API at port %MEAL_API_PORT% — keep both windows open.^)
echo.
start "Home Meal Web" cmd /k "cd /d %~dp0frontend && python -m http.server %LOCAL_WEB_PORT%"

timeout /t 2 /nobreak >nul
start http://localhost:%LOCAL_WEB_PORT%/

echo.
echo If the browser says "site can't be reached", wait a few seconds and refresh.
echo Close the "Home Meal API" and "Home Meal Web" windows to stop.
pause
endlocal
