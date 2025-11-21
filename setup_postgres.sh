#!/bin/bash
# Script to set up PostgreSQL database and user for FinTrack

echo "Setting up PostgreSQL database and user for FinTrack..."

# Check if psql is available
if ! command -v psql &> /dev/null; then
    echo "✗ psql command not found. Please make sure PostgreSQL is installed and in your PATH."
    exit 1
fi

echo "✓ PostgreSQL client found."

# Create the PostgreSQL user and database
echo "Creating database user and database..."

# Create the user and database using psql
psql postgres -c "DO \$\$ 
BEGIN 
  IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = 'fintrack_user') THEN 
    CREATE USER fintrack_user WITH PASSWORD 'fintrack_password';
    ALTER USER fintrack_user CREATEDB;
    RAISE NOTICE 'User fintrack_user created';
  ELSE 
    RAISE NOTICE 'User fintrack_user already exists';
  END IF;
END 
\$\$;"

psql postgres -c "DO \$\$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'fintrack_db') THEN
    CREATE DATABASE fintrack_db OWNER fintrack_user;
    GRANT ALL PRIVILEGES ON DATABASE fintrack_db TO fintrack_user;
    RAISE NOTICE 'Database fintrack_db created';
  ELSE
    RAISE NOTICE 'Database fintrack_db already exists';
  END IF;
END
\$\$;"

if [ $? -eq 0 ]; then
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
else
    echo "✗ PostgreSQL setup failed. Please check the error messages above."
    exit 1
fi