@echo off
echo.
echo  =============================================
echo   HEALTHAPP - First-time setup
echo  =============================================
echo.

set PYTHON=..\..\.venv\Scripts\python.exe
set MANAGE=%PYTHON% manage.py

:: Delete old database if it exists
if exist db.sqlite3 (
    echo [1/6] Deleting old database...
    del /f /q db.sqlite3
) else (
    echo [1/6] No existing database found.
)

:: Create all migrations
echo [2/6] Creating migrations...
%MANAGE% makemigrations accounts patients doctors labs pharmacy services chat notifications
if errorlevel 1 (
    echo ERROR: makemigrations failed!
    pause
    exit /b 1
)

:: Apply migrations
echo [3/6] Applying migrations...
%MANAGE% migrate
if errorlevel 1 (
    echo ERROR: migrate failed!
    pause
    exit /b 1
)

:: Create superuser and seed data
echo [4/6] Seeding sample data...
%MANAGE% seed_data
if errorlevel 1 (
    echo WARNING: seed_data had issues (may be ok if already seeded)
)

:: Collect static files
echo [5/6] Collecting static files...
%MANAGE% collectstatic --noinput

:: Start server
echo [6/6] Starting server...
echo.
echo  ============================================
echo   Server running at: http://127.0.0.1:8000
echo   Admin:   admin@healthapp.local / Admin1234!
echo   Patient: patient1@healthapp.local / Patient1234!
echo  ============================================
echo.
%PYTHON% -m daphne -b 0.0.0.0 -p 8000 healthapp.asgi:application
