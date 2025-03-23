#!/usr/bin/env python
"""
Script to create a test user with an organization
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gdpr_compliance_backend.settings')
django.setup()

from api.models import User, Organization
from django.contrib.auth.hashers import make_password

def create_test_user():
    # Create or get test organization
    org, created = Organization.objects.get_or_create(
        name="Test Organization",
        defaults={
            "industry": "Technology",
            "country": "US",
            "address": "123 Test Street",
            "size": "medium"
        }
    )
    
    if created:
        print(f"Created new organization: {org.name}")
    else:
        print(f"Using existing organization: {org.name}")
    
    # Create or update admin user
    email = "admin@example.com"
    password = "password"
    
    try:
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        print(f"Updated existing user: {email}")
    except User.DoesNotExist:
        user = User.objects.create(
            email=email,
            username=email,
            password=make_password(password),
            is_staff=True,
            is_superuser=True,
            is_active=True,
            organization=org,
            first_name="Admin",
            last_name="User"
        )
        print(f"Created new admin user: {email}")
    
    print(f"\nUser credentials:")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print(f"Organization: {org.name}")

if __name__ == "__main__":
    create_test_user() 