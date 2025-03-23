#!/usr/bin/env python

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gdpr_compliance_backend.settings')
django.setup()

from api.models import DataSubject, DataSubjectRequest

def check_data_state():
    print("=== Data Subject State ===")
    all_subjects = DataSubject.objects.all()
    print(f"Total data subjects: {all_subjects.count()}")
    
    # Check for expired subjects
    print("\nData subjects with [EXPIRED] first name:")
    expired = DataSubject.objects.filter(first_name='[EXPIRED]')
    for subject in expired:
        print(f"- {subject.email} (originally Retention*, anonymized)")
    
    # Check for deleted subjects
    print("\nData subjects with [DELETED] first name:")
    deleted = DataSubject.objects.filter(first_name='[DELETED]')
    for subject in deleted:
        print(f"- {subject.email}")
    
    # Check for subjects with revoked marketing consent
    print("\nData subjects with revoked marketing consent:")
    no_marketing = DataSubject.objects.filter(marketing_consent=False)
    for subject in no_marketing:
        print(f"- {subject.first_name} {subject.last_name} ({subject.email})")
    
    print("\n=== Data Subject Requests State ===")
    all_requests = DataSubjectRequest.objects.all()
    print(f"Total data subject requests: {all_requests.count()}")
    
    # Check for completed requests
    print("\nCompleted requests:")
    completed = DataSubjectRequest.objects.filter(status='completed')
    for request in completed:
        print(f"- {request.data_subject_name} ({request.data_subject_email}): {request.request_type}")
    
    # Check for rejected requests
    print("\nRejected requests:")
    rejected = DataSubjectRequest.objects.filter(status='rejected')
    for request in rejected:
        print(f"- {request.data_subject_name} ({request.data_subject_email}): {request.notes}")
    
    # Check for pending requests
    print("\nPending requests:")
    pending = DataSubjectRequest.objects.filter(status='pending')
    for request in pending:
        print(f"- {request.data_subject_name} ({request.data_subject_email}): {request.request_type}")

if __name__ == '__main__':
    check_data_state() 