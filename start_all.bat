@echo off
echo ===== GDPR Compliance Tool =====
echo Starting both backend and frontend...

echo 1. Starting Django backend in a new window...
start "Django Backend" cmd /k call start_django.bat

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo 2. Starting React frontend...
start "React Frontend" cmd /k call start_react.bat

echo.
echo Both components have been started in separate windows.
echo - Django backend should be running at http://localhost:8000/
echo - React frontend should be running at http://localhost:3000/
echo.
echo Press any key to exit...
pause > nul 