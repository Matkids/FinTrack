import os
import sys
import django
from django.conf import settings

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

try:
    django.setup()
    print("✓ Django setup successful")
    
    # Test importing models
    from app.models import Transaction, Category, Asset, Investment
    print("✓ All models imported successfully")
    
    # Test database connection
    from django.db import connection
    cursor = connection.cursor()
    print("✓ Database connection successful")
    
    # Test that we can query users
    from django.contrib.auth.models import User
    user_count = User.objects.count()
    print(f"✓ User table accessible, found {user_count} users")
    
    print("\nDjango is configured correctly. The issue may be with the development server itself.")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()