#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
python << END
import sys
import time
import psycopg2
from urllib.parse import urlparse
import os
import dj_database_url

# Get database configuration
db_config = dj_database_url.config()
if not db_config:
    print("Error: DATABASE_URL not configured")
    sys.exit(1)

# Extract connection details
dbname = db_config.get('NAME')
user = db_config.get('USER')
password = db_config.get('PASSWORD')
host = db_config.get('HOST')
port = db_config.get('PORT', 5432)

print(f"Attempting to connect to PostgreSQL at {host}...")

# Wait for database to be ready
while True:
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.close()
        print("PostgreSQL is ready!")
        break
    except psycopg2.OperationalError as e:
        print(f"PostgreSQL is not ready yet: {e}")
        time.sleep(1)
END

# Make migrations
echo "Creating migrations..."
python manage.py makemigrations

# Apply migrations
echo "Applying migrations..."
python manage.py migrate --noinput

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

django.setup()
User = get_user_model()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin123!@#')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')

try:
    user = User.objects.create_superuser(username=username, email=email, password=password)
    print('Superuser created successfully')
except Exception as e:
    try:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        print('Superuser password updated successfully')
    except Exception as e:
        print(f'Error handling superuser: {e}')
END 