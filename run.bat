@echo off
echo  Starting HEALTHAPP at http://127.0.0.1:8000
echo  Press Ctrl+C to stop.
echo.
..\..\.venv\Scripts\python.exe -m daphne -b 0.0.0.0 -p 8000 healthapp.asgi:application
