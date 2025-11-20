#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done

echo "PostgreSQL is ready!"
echo "Running Django migrations..."
python manage.py migrate

echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000
