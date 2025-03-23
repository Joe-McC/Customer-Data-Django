@echo off
setlocal EnableDelayedExpansion

echo ===== GDPR Compliance Tool - Auto Debug Startup =====
echo.

set BACKEND_DIR=backend
set FRONTEND_DIR=frontend

REM Create user first to ensure authentication works
echo Creating/updating admin user...
echo @echo off > create_admin.bat
echo cd %BACKEND_DIR% >> create_admin.bat
echo call venv\Scripts\activate >> create_admin.bat
echo python create_admin_user.py >> create_admin.bat
call create_admin.bat
del create_admin.bat

REM Create a temporary backend script
echo @echo off > start_backend.bat
echo cd %BACKEND_DIR% >> start_backend.bat
echo call venv\Scripts\activate >> start_backend.bat
echo python manage.py runserver >> start_backend.bat

REM Create a temporary frontend script with React 18 downgrade and clean install
echo @echo off > start_frontend.bat
echo cd %FRONTEND_DIR% >> start_frontend.bat
echo echo Node.js version: >> start_frontend.bat
echo node -v >> start_frontend.bat
echo echo npm version: >> start_frontend.bat
echo npm -v >> start_frontend.bat
echo echo. >> start_frontend.bat
echo echo Creating .env file with API URL configuration... >> start_frontend.bat
echo echo REACT_APP_API_URL=http://localhost:8000/api/ ^> .env.local >> start_frontend.bat
echo echo Configuring React version... >> start_frontend.bat
echo npm install react@18.2.0 react-dom@18.2.0 --save >> start_frontend.bat
echo echo. >> start_frontend.bat
echo echo Cleaning node_modules... >> start_frontend.bat
echo if exist node_modules rmdir /s /q node_modules >> start_frontend.bat
echo if exist package-lock.json del package-lock.json >> start_frontend.bat
echo echo. >> start_frontend.bat
echo echo Installing dependencies... >> start_frontend.bat
echo npm install >> start_frontend.bat
echo echo. >> start_frontend.bat
echo echo Starting React development server... >> start_frontend.bat
echo npm start >> start_frontend.bat

REM Start backend
echo Starting backend in a new window...
start "GDPR Compliance Backend" cmd /k call start_backend.bat

REM Wait for backend to start
echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

REM Start frontend in current window
echo.
echo.
echo LOGIN INFORMATION:
echo Username: admin@example.com
echo Password: password
echo.
echo Starting frontend with debug output in current window...
echo.
call start_frontend.bat

REM Delete temporary scripts
del start_backend.bat
del start_frontend.bat

echo.
echo Script completed.
echo Press any key to exit...
pause > nul 