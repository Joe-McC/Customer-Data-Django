#!/usr/bin/env python
"""
Test script to verify login functionality
"""

import requests
import json
import os

API_URL = 'http://localhost:8000/api/'

def test_login():
    print("Testing login API...")
    
    # Try with username/email field as per dj-rest-auth spec
    print("\nTrying standard dj-rest-auth login...")
    login_data = {
        'username': 'admin',  # dj-rest-auth expects 'username', not 'email'
        'password': 'password',
    }
    
    try:
        # Send as form data, not JSON
        response = requests.post(f"{API_URL}auth/login/", data=login_data)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            token = response.json().get('key')
            if token:
                print(f"Login successful! Token: {token}")
                return token
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Try alternate formats
    print("\nTrying with JSON format...")
    try:
        response = requests.post(f"{API_URL}auth/login/", json=login_data)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            token = response.json().get('key')
            if token:
                print(f"Login successful! Token: {token}")
                return token
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Try with email as username
    print("\nTrying with email as username...")
    login_data = {
        'username': 'admin@example.com',
        'password': 'password',
    }
    
    try:
        response = requests.post(f"{API_URL}auth/login/", data=login_data)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            token = response.json().get('key')
            if token:
                print(f"Login successful! Token: {token}")
                return token
    except Exception as e:
        print(f"Error: {str(e)}")
    
    return None

def test_user_profile(token):
    print("\nTesting user profile API...")
    
    headers = {
        'Authorization': f'Token {token}'
    }
    
    try:
        response = requests.get(f"{API_URL}users/me/", headers=headers)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("User profile fetch successful!")
            return True
    except Exception as e:
        print(f"Error: {str(e)}")
    
    return False

if __name__ == "__main__":
    token = test_login()
    
    if token:
        test_user_profile(token)
    else:
        print("\nLogin failed with all methods. Please check server logs for details.") 