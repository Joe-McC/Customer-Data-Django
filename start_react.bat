@echo off
cd frontend
echo Setting API URL...
echo REACT_APP_API_URL=http://localhost:8000/api/ > .env
echo Starting React app...
npm start
pause 