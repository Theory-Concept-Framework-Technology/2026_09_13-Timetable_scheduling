@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo Refreshing meal plan database ^(fixes old repeated menu without photos^)...
if exist "data\meals.db" del /f /q "data\meals.db"

call "%~dp0run_local.bat"
