#!/bin/bash
# Script to check and start the Django development server

echo "Checking FinTrack application setup..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found. Please run setup_env.sh first."
    exit 1
fi

echo "Virtual environment found."

# Check if project directory exists
if [ ! -d "project" ]; then
    echo "ERROR: Project directory not found."
    exit 1
fi

echo "Project directory found."

# Activate virtual environment
source venv/bin/activate
echo "Virtual environment activated."

# Navigate to project directory
cd project

# Check if Django is properly installed
echo "Checking Django installation..."
python -c "import django; print('Django version:', django.get_version())" 2>/dev/null || {
    echo "ERROR: Django not found in virtual environment. Please run setup_env.sh again."
    exit 1
}

# Check if the database exists and migrations have been applied
echo "Checking database..."
if [ ! -f "db.sqlite3" ]; then
    echo "Database not found, running migrations..."
    python manage.py migrate
else
    echo "Database found."
fi

# Try to run the server with more verbose output
echo "Starting Django development server on http://127.0.0.1:8000/"
echo "If the server starts successfully, you will see 'Starting development server' message."
echo "Press Ctrl+C to stop the server."
echo ""

# Run server and capture output
python manage.py runserver 8000