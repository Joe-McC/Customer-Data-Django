#!/usr/bin/env python
"""
Script to remove the custom Token class from models.py
This script will scan models.py and remove the Token class that's causing conflicts
"""

import os
import re
import shutil

def main():
    models_file = os.path.join(os.path.dirname(__file__), 'models.py')
    backup_file = os.path.join(os.path.dirname(__file__), 'models.py.bak')
    
    print(f"Looking for models.py at: {models_file}")
    
    if not os.path.exists(models_file):
        print(f"ERROR: Models file not found at {models_file}")
        return
    
    # Create a backup first
    shutil.copy2(models_file, backup_file)
    print(f"Created backup: {backup_file}")
    
    # Read the file content
    with open(models_file, 'r') as f:
        content = f.read()
    
    print(f"File size before processing: {len(content)} bytes")
    
    # Check if the file contains our problematic class
    if "class Token(DefaultToken):" in content:
        print("Found Token class in the file")
    else:
        print("WARNING: Token class not found in file")
        
    if "from rest_framework.authtoken.models import Token as DefaultToken" in content:
        print("Found Token import in the file")
    else:
        print("WARNING: Token import not found in file")
    
    # Find and remove the Token class and its imports
    token_class_pattern = r'\s*# Create a custom Token model that supports UUID fields\s*class Token\(DefaultToken\):.*?(?=\n\S)'
    content_without_token = re.sub(token_class_pattern, '', content, flags=re.DOTALL)
    
    # Remove the imports for the Token class
    import_pattern = r'from rest_framework\.authtoken\.models import Token as DefaultToken\s*'
    content_without_imports = re.sub(import_pattern, '', content_without_token)
    
    # Remove the django.conf settings import if it's not used elsewhere
    if "from django.conf import settings" in content_without_imports and "settings." not in content_without_imports:
        content_without_imports = re.sub(r'from django\.conf import settings\s*', '', content_without_imports)
        print("Removed unused settings import")
    
    print(f"File size after processing: {len(content_without_imports)} bytes")
    
    # Write back the cleaned content if changes were made
    if content != content_without_imports:
        with open(models_file, 'w') as f:
            f.write(content_without_imports)
        print(f"Successfully updated {models_file}")
        print("Please restart the Django server")
    else:
        print("No changes were made to the file")

if __name__ == "__main__":
    main() 