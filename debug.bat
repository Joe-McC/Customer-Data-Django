@echo off
setlocal EnableDelayedExpansion

echo ===== GDPR Compliance Tool - Debug Mode =====

REM Start backend in new window
echo Starting Django backend...
start "Django Backend" cmd /k "cd backend && call venv\Scripts\activate && python manage.py runserver"

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo Backend started in new window.
echo.
echo Starting React frontend with debugging...
echo.

REM Start frontend with React 18
cd frontend
echo Current directory: %CD%
if not exist package.json (
    echo ERROR: package.json not found in %CD%
    goto end
) else (
    echo Found package.json
)

echo Node.js version:
node -v

echo npm version:  
npm -v

echo.
echo Step 1: Configuring environment
echo REACT_APP_API_URL=http://localhost:8000/api/ > .env
echo Created .env file pointing to backend at http://localhost:8000/api/
echo Environment file created

echo.
echo Step 2: Installing stable React version
echo About to install React 18...
call npm install react@18.2.0 react-dom@18.2.0 --save
echo React installation completed with exit code: %ERRORLEVEL%
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install React 18. Check your internet connection.
    goto end
)

echo.
echo Step 3: Cleaning node_modules
if exist node_modules (
    echo Removing node_modules folder...
    rmdir /s /q node_modules
    echo Removed node_modules folder
    if exist package-lock.json (
        echo Removing package-lock.json...
        del package-lock.json
        echo Removed package-lock.json
    )
) else (
    echo No node_modules folder found
)

echo.
echo Step 4: Installing dependencies
echo This may take a few minutes...
echo About to run npm install...
call npm install
echo npm install completed with exit code: %ERRORLEVEL%
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies. Check your internet connection.
    goto end
)

echo.
echo Step 5: Starting React development server
echo About to run npm start...
call npm start
echo npm start completed with exit code: %ERRORLEVEL%

:end
cd ..
echo.
echo Script completed.
pause 