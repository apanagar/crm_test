#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Wait for database to be ready
python << END
import sys
import time
import dj_database_url
import psycopg2
from urllib.parse import urlparse

db_config = dj_database_url.config()
if not db_config:
    print("No DATABASE_URL found, using SQLite")
    sys.exit(0)

db_url = urlparse(db_config['NAME'])
while True:
    try:
        conn = psycopg2.connect(
            dbname=db_url.path[1:],
            user=db_config.get('USER'),
            password=db_config.get('PASSWORD'),
            host=db_url.hostname
        )
        conn.close()
        break
    except psycopg2.OperationalError:
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(1)
print("\nDatabase is ready!")
END

# Make migrations
python manage.py makemigrations

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --no-input

# Create superuser
DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-"admin@example.com"}
DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME:-"admin"}
DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD:-"Admin123!@#"}

python manage.py createsuperuser --noinput || echo "Superuser already exists." 