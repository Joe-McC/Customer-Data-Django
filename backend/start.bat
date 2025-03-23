@echo off
echo ===== GDPR Compliance Tool Setup and Run =====
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

REM Apply migrations
echo Running migrations...
python manage.py migrate

REM Setup test data if requested
set /p setup_data="Do you want to set up test data? (y/n): "
if /i "%setup_data%"=="y" (
    echo Setting up test data...
    python setup_test_data.py
)

REM Run data retention if requested
set /p run_retention="Do you want to run data retention? (y/n): "
if /i "%run_retention%"=="y" (
    set /p dry_run="Run in dry-run mode? (y/n): "
    if /i "%dry_run%"=="y" (
        echo Running data retention in dry-run mode...
        python manage.py data_retention --dry-run
    ) else (
        echo Running data retention...
        python manage.py data_retention
    )
)

REM Check data state if requested
set /p check_data="Do you want to check the data state? (y/n): "
if /i "%check_data%"=="y" (
    echo Checking data state...
    python check_data_state.py
)

REM Set up cron job if requested
set /p setup_cron="Do you want to setup the cron job for data retention? (y/n): "
if /i "%setup_cron%"=="y" (
    echo Setting up scheduled task...
    python manage.py crontab add
)

REM Start the server
set /p start_server="Do you want to start the Django server? (y/n): "
if /i "%start_server%"=="y" (
    echo Starting Django development server...
    python manage.py runserver
) else (
    echo Setup complete. To start the server manually, run:
    echo python manage.py runserver
)

REM Keep the window open if we didn't start the server
if /i NOT "%start_server%"=="y" (
    echo.
    echo Press any key to exit...
    pause > nul
) 