#!/usr/bin/env python
"""
Script to create or update an admin user with known credentials
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gdpr_compliance_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from api.models import Organization, User
import uuid

def create_or_update_admin():
    print('Creating or updating admin user...')
    
    # First, make sure we have an organization
    try:
        org = Organization.objects.get(name='Test Organization')
        print(f'Found existing organization: {org.name}')
    except Organization.DoesNotExist:
        print('Creating new test organization')
        org = Organization.objects.create(
            name='Test Organization',
            address='123 Test Street, Test City',
            registration_number='TEST12345',
            industry='consulting'
        )
    
    # Define credentials
    admin_email = 'admin@example.com'
    admin_password = 'password'
    
    # Try to find existing user
    User = get_user_model()
    try:
        user = User.objects.get(email=admin_email)
        print(f'Found existing user: {user.username} ({user.email})')
        
        # Make sure user has the right permissions
        user.is_staff = True
        user.is_admin = True
        
        # Reset password to known value
        user.set_password(admin_password)
        user.save()
        print('User password has been reset')
        
    except User.DoesNotExist:
        print(f'Creating new admin user with email: {admin_email}')
        with transaction.atomic():
            user = User.objects.create_user(
                username='admin',
                email=admin_email,
                password=admin_password,
                first_name='Admin',
                last_name='User',
                organization=org,
                is_staff=True,
                is_admin=True,
                is_superuser=True,
            )
    
    print(f"""
    Admin user created/updated successfully!
    
    Login with:
    Email: {admin_email}
    Password: {admin_password}
    Organization: {org.name}
    """)
    
    # Create auth token for the user
    from rest_framework.authtoken.models import Token
    token, created = Token.objects.get_or_create(user=user)
    if created:
        print(f'Created new auth token for user')
    else:
        print(f'Using existing auth token for user')
    
    print(f'Auth token: {token.key}')
    
    return user, token

if __name__ == '__main__':
    user, token = create_or_update_admin() 