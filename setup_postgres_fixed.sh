#!/bin/bash
# Script to set up PostgreSQL database and user for FinTrack

echo "Setting up PostgreSQL database and user for FinTrack..."

# Check if psql is available
if ! command -v psql &> /dev/null; then
    echo "✗ psql command not found. Please make sure PostgreSQL is installed and in your PATH."
    exit 1
fi

echo "✓ PostgreSQL client found."

# Create the user first
echo "Creating database user fintrack_user..."
createuser_result=$(psql postgres -c "CREATE USER fintrack_user WITH PASSWORD 'fintrack_password';" 2>&1)
if [ $? -eq 0 ] || [[ "$createuser_result" == *"already exists"* ]]; then
    if [[ "$createuser_result" == *"already exists"* ]]; then
        echo "✓ User fintrack_user already exists"
    else
        echo "✓ User fintrack_user created"
    fi
else
    echo "✗ Failed to create user: $createuser_result"
    exit 1
fi

# Alter user to allow database creation
echo "Granting database creation rights to fintrack_user..."
psql postgres -c "ALTER USER fintrack_user CREATEDB;" 2>/dev/null

# Create the database
echo "Creating database fintrack_db..."
createdb_result=$(psql postgres -c "CREATE DATABASE fintrack_db OWNER fintrack_user;" 2>&1)
if [ $? -eq 0 ] || [[ "$createdb_result" == *"already exists"* ]]; then
    if [[ "$createdb_result" == *"already exists"* ]]; then
        echo "✓ Database fintrack_db already exists"
    else
        echo "✓ Database fintrack_db created"
    fi
else
    echo "✗ Failed to create database: $createdb_result"
    exit 1
fi

# Grant privileges
echo "Granting privileges..."
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE fintrack_db TO fintrack_user;" 2>/dev/null

echo "✓ PostgreSQL database and user setup completed successfully!"
echo ""
echo "Database: fintrack_db"
echo "User: fintrack_user"
echo "Password: fintrack_password"
echo "Host: localhost"
echo "Port: 5432"
echo ""
echo "Now run the following commands to set up Django:"
echo "cd project"
echo "python manage.py migrate"
echo "python manage.py createsuperuser"
echo "python manage.py runserver"