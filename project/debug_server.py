import os
import sys
from django.core.management import execute_from_command_line
from django.conf import settings

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

print("Starting Django server...")
print(f"Settings module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

if __name__ == "__main__":
    print("sys.argv:", sys.argv)
    execute_from_command_line(['manage.py', 'runserver', '8000'])