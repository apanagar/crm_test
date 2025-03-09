#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Create database directory if it doesn't exist
mkdir -p /opt/render/project/src/data

# Make migrations
echo "Creating migrations..."
python manage.py makemigrations

# Run migrations
echo "Applying migrations..."
SQLITE_PATH=/opt/render/project/src/data/db.sqlite3
export SQLITE_PATH
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Create superuser
echo "Creating superuser..."
DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-"admin@example.com"}
DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME:-"admin"}
DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD:-"Admin123!@#"}

python manage.py createsuperuser --noinput || echo "Superuser already exists." 