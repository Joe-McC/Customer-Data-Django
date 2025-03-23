# Data Retention Feature

The data retention feature automates the enforcement of data retention policies in compliance with GDPR and other privacy regulations. It provides mechanisms to:

1. Process expired consent records
2. Handle deletion requests
3. Anonymize data that has reached its retention period

## How It Works

The data retention system operates through a Django management command that can be scheduled to run automatically via a cron job. The command processes three main types of data:

### 1. Expired Consent Records

- Marketing consent is considered expired after 2 years (configurable)
- When consent expires, the system:
  - Sets the consent flag to `False`
  - Logs the activity in the `ConsentActivity` table

### 2. Pending Deletion Requests

- Processes deletion requests older than 30 days (configurable)
- For each request, the system:
  - Identifies the associated data subject
  - Anonymizes personal data by replacing it with markers like "[DELETED]"
  - Revokes all consent flags
  - Updates the request status to "completed"
  - If no matching data subject is found, marks the request as "rejected"

### 3. Data Beyond Retention Period

- Identifies records that have passed their expiry date (`data_expiry_date`)
- For expired records, the system:
  - Anonymizes personal data by replacing it with markers like "[EXPIRED]"
  - Anonymizes the email while maintaining a reference to the original record
  - Revokes all consent flags
  - Adds a note indicating the reason for anonymization

## Usage

### Running the Command Manually

To run the data retention process manually:

```
python manage.py data_retention
```

To run in dry-run mode (preview changes without making them):

```
python manage.py data_retention --dry-run
```

### Scheduling with Cron

The data retention process is scheduled to run daily at 3 AM using Django Crontab. This configuration is defined in the Django settings:

```python
CRONJOBS = [
    ('0 3 * * *', 'django.core.management.call_command', ['data_retention'], {}, '>> /var/log/data_retention.log 2>&1')
]
```

### Logging

The command produces detailed logging, including:
- Number of records processed
- Types of processing applied
- Errors encountered

## Configuration

The data retention policies can be configured by modifying constants in the command:

1. **Marketing Consent Expiry**: Currently set to 730 days (2 years)
2. **Deletion Request Age**: Currently set to 30 days before processing
3. **Data Retention Period**: Configurable per organization or data type

## Testing

Test data can be generated using the `setup_test_data.py` script, which creates:
- Data subjects with expired marketing consent
- Data subjects beyond their retention period
- Pending deletion requests (valid and invalid)

To check the state of the data after running the command, use `check_data_state.py`.

## Implementation Details

The implementation follows these principles:

1. **Atomic Transactions**: All changes are wrapped in transactions to ensure data integrity
2. **Error Handling**: Each processing step handles exceptions separately to prevent complete failure
3. **Audit Trail**: Activities are logged for compliance and audit purposes
4. **Dry-Run Mode**: Changes can be previewed before actual execution

## Performance Considerations

The command processes records in batches to manage memory usage and database load. For large datasets, consider:

1. Running the command during off-peak hours
2. Adjusting batch sizes if necessary
3. Monitoring execution time and resource usage 