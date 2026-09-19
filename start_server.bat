@echo off
cd /d "%~dp0"
echo Starting Evently Development Server...
call .venv\Scripts\activate.bat
cd backend
python manage.py runserver 127.0.0.1:8000
pause
