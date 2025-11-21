#!/usr/bin/env python
"""
Diagnostic script to check Django application setup and PostgreSQL connection
"""
import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line
from django.db import connection

def check_django_setup():
    """Check if Django can be properly configured"""
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
        django.setup()
        print("✓ Django setup successful")
        return True
    except Exception as e:
        print(f"✗ Django setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database_connection():
    """Check if we can connect to the database"""
    try:
        # This will attempt to connect to the database
        c = connection.cursor()
        print("✓ PostgreSQL connection successful")
        return True
    except Exception as e:
        print(f"✗ PostgreSQL connection failed: {e}")
        print("Make sure PostgreSQL is running and credentials are correct")
        print("Check your .env file and project/settings.py database configuration")
        return False

def check_tables_exist():
    """Check if Django tables exist in the database"""
    try:
        from django.contrib.auth.models import User
        user_count = User.objects.count()
        print(f"✓ Database tables exist (found {user_count} users)")
        return True
    except Exception as e:
        print(f"✗ Database tables may not exist: {e}")
        print("Run 'python manage.py migrate' to create tables")
        return False

def main():
    print("FinTrack Django Application Diagnostic")
    print("=====================================")
    
    # Check Django setup
    django_ok = check_django_setup()
    if not django_ok:
        return
    
    # Check database connection
    db_ok = check_database_connection()
    if not db_ok:
        return
    
    # Check if tables exist
    tables_ok = check_tables_exist()
    if not tables_ok:
        print("\nTo fix the database tables:")
        print("1. Make sure you're in the 'project' directory")
        print("2. Run: python manage.py migrate")
        print("3. Then: python manage.py createsuperuser")
        return
    
    print("\n✓ All checks passed! The server should be able to start.")
    print("\nTo start the server:")
    print("1. Make sure you're in the project directory")
    print("2. Run: python manage.py runserver")
    print("\nThe application will be available at http://127.0.0.1:8000/")

if __name__ == '__main__':
    main()