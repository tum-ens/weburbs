#!/bin/sh

echo "Waiting for database..."

while ! nc -z $SQL_HOST $SQL_PORT; do
  sleep 1
done

echo "Database started"

python manage.py flush --no-input
python manage.py migrate

exec "$@"
