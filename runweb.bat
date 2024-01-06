@echo off
powershell -ExecutionPolicy Bypass -File call ..\env\Scripts\Activate.ps1
python manage.py runserver 0.0.0.0:8000