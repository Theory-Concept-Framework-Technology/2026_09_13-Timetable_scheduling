@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

set WEB_PORT=8000
if exist .env (
    for /f "usebackq tokens=1,* delims==" %%a in (`findstr /b /i "WEB_PORT=" .env`) do set WEB_PORT=%%b
)

if not exist .env copy .env.example .env

where docker >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not on PATH.
    echo Use run_local.bat instead.
    goto :fail
)

docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running.
    goto :fail
)

echo Building and starting containers on host port %WEB_PORT% ...
docker compose up --build -d
if errorlevel 1 goto :fail

timeout /t 5 /nobreak >nul
docker compose ps
echo.
echo Home Meal Planner: http://localhost:%WEB_PORT%/
echo Health:            http://localhost:%WEB_PORT%/api/meals/health
echo.
echo To stop: docker compose down
goto :done

:fail
echo.
pause
exit /b 1

:done
pause
endlocal
