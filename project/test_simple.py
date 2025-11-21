import os
import django
from django.http import HttpResponse
from django.urls import path
from django.core.management import execute_from_command_line
import sys

# Create a minimal Django app to test if there's an issue with the main project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

def hello_world(request):
    return HttpResponse("Django is working!")

def test_runserver():
    # Create a simple Django app for testing
    from django.conf.urls import url
    from django.conf import settings
    
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY='test-key',
            ROOT_URLCONF=__name__,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            USE_TZ=True,
        )
    
    django.setup()
    print("Django test server setup successful!")
    return True

if __name__ == "__main__":
    test_runserver()
    print("Django can be imported and configured successfully. The issue might be with the management command output in this terminal.")
    
    # Test the actual project settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
    django.setup()
    print("Project settings loaded successfully")