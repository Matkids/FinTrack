import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

# Set password for admin user
from django.contrib.auth.models import User

# Get or create admin user
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@example.com',
        'is_staff': True,
        'is_superuser': True
    }
)

if created:
    print("Admin user created.")
else:
    print("Admin user already exists.")

# Set the password
admin_user.set_password('admin123')
admin_user.save()
print("Admin password set to 'admin123'")
print("You can now log in to the application with:")
print("Username: admin")
print("Password: admin123")