#!/usr/bin/env python
"""
Script to directly fix the auth token table using SQL
"""
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def fix_token_table():
    # Get database credentials from environment or use defaults
    db_name = os.environ.get('DB_NAME', 'gdpr_db_django')
    db_user = os.environ.get('DB_USER', 'postgres')
    db_password = os.environ.get('DB_PASSWORD', 'Oscar1000!')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432')
    
    print(f"Connecting to database {db_name} on {db_host}:{db_port}...")
    
    # Connect to the database
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("Successfully connected to the database.")
        
        # First, check the current type
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
        
        # Find the constraint name
        print("Finding foreign key constraints...")
        cursor.execute("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'authtoken_token'
            AND constraint_type = 'FOREIGN KEY'
        """)
        
        fk_constraints = cursor.fetchall()
        print(f"Found constraints: {fk_constraints}")
        
        # Delete any existing tokens to avoid conversion issues
        print("Deleting existing tokens...")
        cursor.execute("DELETE FROM authtoken_token")
        
        # Drop all foreign key constraints on the table
        for constraint in fk_constraints:
            constraint_name = constraint[0]
            print(f"Dropping constraint: {constraint_name}")
            cursor.execute(f"""
                ALTER TABLE authtoken_token DROP CONSTRAINT IF EXISTS "{constraint_name}"
            """)
        
        # Change the column type
        print("Changing column type to UUID...")
        cursor.execute("""
            ALTER TABLE authtoken_token 
            ALTER COLUMN user_id TYPE uuid USING NULL
        """)
        
        # Add back the foreign key constraint
        print("Adding foreign key constraint...")
        cursor.execute("""
            ALTER TABLE authtoken_token
            ADD CONSTRAINT authtoken_token_user_id_fkey
            FOREIGN KEY (user_id)
            REFERENCES api_user(id)
            ON DELETE CASCADE
        """)
        
        print("Successfully fixed the authtoken_token table!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    fix_token_table() 