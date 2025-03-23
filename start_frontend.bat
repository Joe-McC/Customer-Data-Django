@echo off 
cd frontend 
echo Node.js version: 
node -v 
echo npm version: 
npm -v 
echo. 
echo Creating .env file with API URL configuration... 
echo REACT_APP_API_URL=http://localhost:8000/api/ > .env 
echo Configuring React version... 
npm install react@18.2.0 react-dom@18.2.0 --save 
echo. 
echo Cleaning node_modules... 
if exist node_modules rmdir /s /q node_modules 
if exist package-lock.json del package-lock.json 
echo. 
echo Installing dependencies... 
npm install 
echo. 
echo Starting React development server... 
npm start 
