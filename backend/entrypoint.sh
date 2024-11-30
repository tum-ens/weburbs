#!/bin/sh

echo "Waiting for database..."

while ! nc -z $SQL_HOST $SQL_PORT; do
  sleep 1
done

echo "Database started"

python manage.py migrate

gunicorn backendurbs.wsgi:application --bind 0.0.0.0:8000
