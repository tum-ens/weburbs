#!/bin/sh

echo "Waiting for database..."

while ! nc -z $SQL_HOST $SQL_PORT; do
  sleep 1
done

echo "Database started"

python manage.py migrate
python manage.py load_config
python manage.py sync_admin_users
python manage.py purge_rejected_users
python manage.py purge_unverified_users

gunicorn backendurbs.wsgi:application --bind 0.0.0.0:8000 --timeout 600
