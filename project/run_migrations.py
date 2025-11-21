import os
import django
from django.core.management import execute_from_command_line
import sys

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

# Import migration management
from django.core.management.commands.migrate import Command as MigrateCommand
from django.db.migrations.executor import MigrationExecutor
from django.db import connections

def check_migrations():
    """Check migration status"""
    connection = connections['default']
    executor = MigrationExecutor(connection)
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    return plan

def run_migrations():
    """Run migrations"""
    try:
        # Show current migration status
        plan = check_migrations()
        if plan:
            print(f"Found {len(plan)} unapplied migrations:")
            for migration, backwards in plan:
                print(f"  - {migration}")
        else:
            print("No unapplied migrations")
        
        # Run migrate command
        sys.argv = ['manage.py', 'migrate']
        execute_from_command_line(sys.argv)
        print("Migrations completed successfully!")
        
    except Exception as e:
        print(f"Error running migrations: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_migrations()