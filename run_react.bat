@echo off
cd frontend
echo Current directory: %CD%

echo "Step 1: Installing React 18"
npm install react@18.2.0 react-dom@18.2.0 --save

echo "Step 2: Clean install"
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del package-lock.json
echo "Cleaned node_modules"

echo "Step 3: Installing dependencies"
npm install

echo "Step 4: Setting up environment"
echo REACT_APP_API_URL=http://localhost:8000/api/ > .env

echo "Step 5: Starting React"
npm start

pause 