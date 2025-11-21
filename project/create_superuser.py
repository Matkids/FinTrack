import os
import django
from django.contrib.auth import get_user_model

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

# Create superuser
User = get_user_model()

username = 'admin'
email = 'admin@example.com'
password = 'admin123'

# Check if user already exists
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'Superuser {username} created successfully!')
else:
    print(f'Superuser {username} already exists.')