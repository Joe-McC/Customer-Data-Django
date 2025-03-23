#!/usr/bin/env python
"""
Script to fix authentication token model compatibility with UUID users
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gdpr_compliance_backend.settings')
django.setup()

from django.db import connection

def fix_token_model():
    print("Fixing authtoken_token model to work with UUID user IDs...")
    
    # First check if there's a type mismatch
    with connection.cursor() as cursor:
        # Check database type - this SQL is PostgreSQL specific
        cursor.execute("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'authtoken_token' 
            AND column_name = 'user_id'
        """)
        result = cursor.fetchone()
        
        if not result:
            print("Error: Could not find the authtoken_token table or user_id column")
            return
            
        current_type = result[0]
        print(f"Current user_id type: {current_type}")
        
        if current_type.lower() == 'uuid':
            print("Field already fixed (UUID type)")
            return
            
        # Change the column type to UUID
        print("Altering column type to UUID...")
        try:
            # Drop any existing tokens first (to avoid conversion issues)
            cursor.execute("DELETE FROM authtoken_token")
            
            # Modify the column type
            cursor.execute("""
                ALTER TABLE authtoken_token 
                ALTER COLUMN user_id TYPE uuid USING NULL
            """)
            
            # Re-create the foreign key constraint
            cursor.execute("""
                ALTER TABLE authtoken_token
                ADD CONSTRAINT authtoken_token_user_id_fkey
                FOREIGN KEY (user_id)
                REFERENCES api_user(id)
                ON DELETE CASCADE
            """)
            
            print("Successfully fixed the authtoken_token table!")
        except Exception as e:
            print(f"Error fixing the table: {e}")

if __name__ == "__main__":
    fix_token_model() 