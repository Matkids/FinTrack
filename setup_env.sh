#!/bin/bash
# Script to set up the Django project environment

echo "Setting up Django project environment..."

# Create virtual environment using standard naming
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install project dependencies
echo "Installing project dependencies..."
pip install -r requirements.txt

# Verify installations
echo "Verifying installations..."
python -c "import django; print('Django version:', django.get_version())" 2>/dev/null || echo "Django not installed properly"
python -c "import decouple; print('python-decouple: OK')" 2>/dev/null || echo "python-decouple not installed properly"

echo "Virtual environment setup complete!"
echo "To activate the environment in the future, use: source venv/bin/activate"
echo "To start the Django server: cd project && python manage.py runserver"