# GDPR Compliance Tool

This Django application helps organizations manage their GDPR compliance processes, including data retention policies.

## Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd django_grpc/backend
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure database settings in `.env` or in `settings.py`

4. Run migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

## Data Retention Feature

The data retention feature automates the enforcement of data retention policies in compliance with GDPR and other privacy regulations.

### Running the Data Retention Command

To manually run the data retention process:

```
python manage.py data_retention
```

To preview changes without actually modifying data (dry-run mode):

```
python manage.py data_retention --dry-run
```

### What the Data Retention Command Does

The command processes three types of data:

1. **Expired Consent Records**: Identifies and revokes marketing consent older than 2 years
2. **Pending Deletion Requests**: Processes subject deletion requests that are older than 30 days
3. **Data Beyond Retention Period**: Anonymizes records that have passed their expiry date

### Testing with Sample Data

You can create test data to see how the data retention process works:

```
python setup_test_data.py
```

This will create:
- Data subjects with expired marketing consent
- Data subjects beyond their retention period
- Pending deletion requests

To check the state of your data after running the retention command:

```
python check_data_state.py
```

### Scheduling Automatic Execution

The data retention process is configured to run automatically every day at 3 AM using Django Crontab.

To install the scheduled job:

```
python manage.py crontab add
```

To show currently configured cron jobs:

```
python manage.py crontab show
```

To remove the cron jobs:

```
python manage.py crontab remove
```

## Other Features

- Document template management
- Data subject request processing
- Consent tracking
- Automated GDPR workflows

For more detailed documentation, see the `docs/` directory. 