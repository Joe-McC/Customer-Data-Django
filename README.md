# GDPR Compliance SaaS for Professional Services

A SaaS application to help professional services firms manage GDPR compliance requirements efficiently.

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

## Getting Started

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver