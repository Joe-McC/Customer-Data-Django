# GDPR Compliance Tool

A comprehensive tool for managing GDPR compliance, including data retention, consent management, and data subject request processing.

## System Requirements

- Python 3.8+
- Node.js 14+ and npm
- PostgreSQL database
- Windows (for the start.bat script) or equivalent commands for other OS

## Quick Start

The easiest way to run the application is to use the provided `start.bat` script:

1. Clone the repository
2. Open Command Prompt
3. Navigate to the project root directory
4. Run `start.bat`
5. Choose option 3 to start both frontend and backend

## Manual Setup

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   ```
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Unix/Mac
   ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Set up test data (optional):
   ```
   python setup_test_data.py
   ```

7. Start the Django server:
   ```
   python manage.py runserver
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Create a `.env` file with:
   ```
   REACT_APP_API_URL=http://localhost:8000/api/
   ```

3. Install dependencies:
   ```
   npm install
   ```

4. Start the development server:
   ```
   npm start
   ```

## Data Retention Feature

The data retention feature ensures compliance with GDPR data retention policies by automating:

1. Processing expired consent records
2. Handling deletion requests
3. Anonymizing data beyond retention periods

### Running the Data Retention Command

```
cd backend
python manage.py data_retention  # Run the command
python manage.py data_retention --dry-run  # Preview without changes
```

### Scheduling Automatic Execution

The data retention process is scheduled to run daily at 3 AM using Django Crontab:

```
python manage.py crontab add  # Add to crontab
python manage.py crontab show  # View scheduled jobs
python manage.py crontab remove  # Remove from crontab
```

## Troubleshooting

### Backend Connection Issues

If the frontend cannot connect to the backend:

1. Ensure the backend server is running on port 8000
2. Check that CORS is properly configured in `backend/gdpr_compliance_backend/settings.py`
3. Verify the API URL in `frontend/.env` is correct

### React Component Errors

If you see JSX/component errors:

1. Check all component import statements
2. Ensure components are properly exported
3. Make sure you're not mixing default and named exports/imports

### Database Issues

If you encounter database errors:

1. Check PostgreSQL connection settings in `.env` or `settings.py`
2. Ensure the database exists and is accessible
3. Run migrations again: `python manage.py migrate`

## Features

- Data mapping and inventory management
- Data subject request handling
- Compliance documentation generation
- Dashboard with compliance metrics
- Secure multi-tenant architecture

## Technology Stack

- Backend: Django, PostgreSQL
- Frontend: React, Material-UI
- Authentication: JWT

[Client Browser] ← HTTPS → [CloudFront] → [Application Load Balancer]
                                            ↓
[S3 Storage] ← → [Django API + Web Server] ← → [PostgreSQL Database]
                     ↑         ↑
                     ↓         ↓
              [Redis Cache]   [AWS SES Email]

## Getting Started

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

cd ../frontend
npm install
npm start