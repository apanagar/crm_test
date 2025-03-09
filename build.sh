#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Verify database configuration
echo "Verifying database configuration..."
python << END
import os
import sys
import dj_database_url

print("Checking DATABASE_URL...")
database_url = os.environ.get('DATABASE_URL', '')
if database_url:
    print(f"DATABASE_URL exists (first 20 chars): {database_url[:20]}...")
    config = dj_database_url.config()
    print("Database config:", config)
    if not config:
        print("Error: Could not parse DATABASE_URL")
        sys.exit(1)
    print("Database configuration is valid")
else:
    print("No DATABASE_URL found, will use SQLite")
END

# Make migrations
echo "Creating migrations..."
python manage.py makemigrations

# Apply migrations
echo "Applying migrations..."
python manage.py migrate --noinput

# Verify database tables
echo "Verifying database tables..."
python << END
import django
from django.db import connection

django.setup()

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    print("Available tables:", [table[0] for table in tables])
END

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Create superuser
echo "Creating superuser..."
DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-"admin@example.com"}
DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME:-"admin"}
DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD:-"Admin123!@#"}

# Try to create superuser, if it fails, try to update password
python << END
import os
import django
from django.contrib.auth import get_user_model
from django.db import connection

django.setup()
User = get_user_model()

# First verify the auth_user table exists
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'auth_user'
        );
    """)
    table_exists = cursor.fetchone()[0]
    print(f"auth_user table exists: {table_exists}")

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin123!@#')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')

try:
    user = User.objects.create_superuser(username=username, email=email, password=password)
    print('Superuser created successfully')
except Exception as e:
    print(f'Error creating superuser: {e}')
    try:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        print('Superuser password updated successfully')
    except Exception as e:
        print(f'Error updating superuser: {e}')
END 