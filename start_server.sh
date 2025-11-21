#!/bin/bash
# Script to start the Django development server with environment variables

echo "Starting FinTrack application..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run setup_env.sh first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Using default settings."
else
    echo "Loading environment variables from .env file..."
    export $(cat .env | xargs)
fi

# Activate virtual environment
source venv/bin/activate

echo "Virtual environment activated."

# Navigate to project directory
cd project

# Set Django settings module
export DJANGO_SETTINGS_MODULE=project.settings

echo "Starting Django development server on http://127.0.0.1:8000/"
echo "Server logs will appear below:"
echo "Press Ctrl+C to stop the server."
echo ""

# Start the server with the environment variables
exec python manage.py runserver 8000