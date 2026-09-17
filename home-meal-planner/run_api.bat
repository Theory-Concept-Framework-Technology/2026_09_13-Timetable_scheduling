@echo off
setlocal
cd /d "%~dp0"
pip install -r requirements.txt
set PYTHONPATH=%CD%\backend
set MEAL_DB_PATH=%CD%\data\meals.db
set MEAL_CACHE_DIR=%CD%\data\meal_cache
if not exist data mkdir data
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
