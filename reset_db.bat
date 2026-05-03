@echo off
echo.
echo  Resetting database...
echo.

set PYTHON=..\..\.venv\Scripts\python.exe
set MANAGE=%PYTHON% manage.py

if exist db.sqlite3 del /f /q db.sqlite3
echo  Old database deleted.

%MANAGE% makemigrations accounts patients doctors labs pharmacy services chat notifications
%MANAGE% migrate
%MANAGE% seed_data

echo.
echo  Done! Start server with: run.bat
pause
