#!/usr/bin/env python

import os
import django
from datetime import datetime, timedelta
import uuid
import time

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gdpr_compliance_backend.settings')
django.setup()

from django.utils import timezone
from api.models import Organization, DataSubject, DataSubjectRequest

def create_test_data():
    print("Creating test data for data retention...")
    
    # Generate timestamp to make email addresses unique
    timestamp = int(time.time())
    
    # Create a test organization
    try:
        organization = Organization.objects.get(name="Test Organization")
        print("Using existing organization: Test Organization")
    except Organization.DoesNotExist:
        organization = Organization.objects.create(
            name="Test Organization",
            address="123 Test Street, Test City, 12345",
            registration_number="TEST12345",
            industry="consulting"
        )
        print("Created organization: Test Organization")
    
    # Create data subjects with expired marketing consent
    expired_consent_count = 0
    for i in range(3):
        # Use unique email with timestamp
        email = f"expired{i}_{timestamp}@example.com"
        
        # Check if it already exists
        if DataSubject.objects.filter(email=email).exists():
            print(f"Skipping: Data subject with email {email} already exists")
            continue
        
        data_subject = DataSubject(
            organization=organization,
            first_name=f"Expired{i}",
            last_name="Consent",
            email=email,
            phone=f"+1234567890{i}",
            marketing_consent=True,
            marketing_consent_date=timezone.now() - timedelta(days=800),  # Older than 2 years
            data_processing_consent=True,
            data_processing_consent_date=timezone.now(),
            cookie_consent=True,
            cookie_consent_date=timezone.now(),
            privacy_notice_version="1.0",
            privacy_notice_accepted_date=timezone.now(),
            notes="Test data subject with expired marketing consent"
        )
        data_subject.save()
        expired_consent_count += 1
    print(f"Created {expired_consent_count} data subjects with expired marketing consent")
    
    # Create data subjects with expired data (beyond retention period)
    expired_data_count = 0
    for i in range(2):
        # Use unique email with timestamp
        email = f"retention{i}_{timestamp}@example.com"
        
        # Check if it already exists
        if DataSubject.objects.filter(email=email).exists():
            print(f"Skipping: Data subject with email {email} already exists")
            continue
            
        data_subject = DataSubject(
            organization=organization,
            first_name=f"Retention{i}",
            last_name="Limit",
            email=email,
            phone=f"+2234567890{i}",
            marketing_consent=True,
            marketing_consent_date=timezone.now(),
            data_processing_consent=True,
            data_processing_consent_date=timezone.now(),
            cookie_consent=True,
            cookie_consent_date=timezone.now(),
            privacy_notice_version="1.0",
            privacy_notice_accepted_date=timezone.now(),
            data_expiry_date=timezone.now() - timedelta(days=10),  # Expired 10 days ago
            notes="Test data subject beyond retention period"
        )
        data_subject.save()
        expired_data_count += 1
    print(f"Created {expired_data_count} data subjects beyond retention period")
    
    # Create pending deletion requests
    deletion_requests_count = 0
    
    # First create a data subject to delete
    delete_email = f"delete.me_{timestamp}@example.com"
    
    # Check if it already exists
    if not DataSubject.objects.filter(email=delete_email).exists():
        data_subject = DataSubject(
            organization=organization,
            first_name="Delete",
            last_name="Me",
            email=delete_email,
            phone="+3334567890",
            marketing_consent=True,
            marketing_consent_date=timezone.now(),
            data_processing_consent=True,
            data_processing_consent_date=timezone.now(),
            cookie_consent=True,
            cookie_consent_date=timezone.now(),
            privacy_notice_version="1.0",
            privacy_notice_accepted_date=timezone.now(),
            notes="Test data subject for deletion request"
        )
        data_subject.save()
        
        # Then create the deletion request
        deletion_request = DataSubjectRequest.objects.create(
            organization=organization,
            request_type="deletion",
            data_subject_name="Delete Me",
            data_subject_email=delete_email,
            request_details="Please delete all my data",
            date_received=timezone.now() - timedelta(days=35),  # Older than 30 days
            status="pending",
            due_date=timezone.now() - timedelta(days=5),  # Past due
            notes="Pending deletion request for testing"
        )
        deletion_requests_count += 1
        print(f"Created deletion request for {delete_email}")
    else:
        print(f"Skipping: Data subject with email {delete_email} already exists")
    
    # Create an invalid deletion request (no matching data subject)
    notfound_email = f"notfound_{timestamp}@example.com"
    invalid_request = DataSubjectRequest.objects.create(
        organization=organization,
        request_type="deletion",
        data_subject_name="Not Found",
        data_subject_email=notfound_email,
        request_details="Please delete all my data",
        date_received=timezone.now() - timedelta(days=40),  # Older than 30 days
        status="pending",
        due_date=timezone.now() - timedelta(days=10),  # Past due
        notes="Pending deletion request with no matching data subject"
    )
    deletion_requests_count += 1
    print(f"Created 1 invalid deletion request for {notfound_email}")
    
    print(f"Total test records created: {expired_consent_count + expired_data_count + deletion_requests_count}")
    print("\nYou can now run the data retention command with:")
    print("python manage.py data_retention --dry-run")
    print("python manage.py data_retention")

if __name__ == '__main__':
    create_test_data() 