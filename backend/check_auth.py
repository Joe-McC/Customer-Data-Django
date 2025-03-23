#!/usr/bin/env python
"""
Script to check authentication and verify user credentials
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gdpr_compliance_backend.settings')
django.setup()

from api.models import User
from django.contrib.auth import authenticate

def check_auth():
    # Check admin user existence
    email = "admin@example.com"
    password = "password"
    
    try:
        user = User.objects.get(email=email)
        print(f"Found user in database: {email}")
        print(f"User details:")
        print(f"- Username: {user.username}")
        print(f"- Email: {user.email}")
        print(f"- Is active: {user.is_active}")
        print(f"- Is staff: {user.is_staff}")
        print(f"- Is superuser: {user.is_superuser}")
        print(f"- Organization: {user.organization.name if user.organization else 'None'}")
        
        # Try to authenticate
        auth_user = authenticate(username=email, password=password)
        if auth_user:
            print("\nAuthentication successful!")
            print(f"Authenticated user: {auth_user.email}")
        else:
            print("\nAuthentication failed!")
            print("User exists but password may be incorrect or account is inactive")
            
            # For debugging purposes only - DO NOT use in production!
            from django.contrib.auth.hashers import check_password
            if check_password(password, user.password):
                print("Password hash matches - issue might be with the authentication backend")
            else:
                print("Password hash does not match - password is incorrect")
                
    except User.DoesNotExist:
        print(f"User with email {email} not found in database!")
        
    # List all users for debugging
    print("\nAll users in database:")
    for user in User.objects.all():
        print(f"- {user.email} (Organization: {user.organization.name if user.organization else 'None'})")

if __name__ == "__main__":
    check_auth() 