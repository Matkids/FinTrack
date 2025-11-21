#!/usr/bin/env python3
import os
import django
from django.core.management import execute_from_command_line

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

if __name__ == '__main__':
    django.setup()
    
    # Print confirmation that Django has been set up
    print("Django setup completed successfully")
    
    # Try to run the server
    import sys
    sys.argv = ['manage.py', 'runserver', '8000', '--noreload']
    
    try:
        execute_from_command_line(sys.argv)
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()