#!/bin/bash -e

echo "Running migrations"
python django_app/manage.py migrate
python django_app/manage.py collectstatic --no-input

# Start webserver
echo "Running in DBT Platform"
gunicorn django_app.config.wsgi --config django_app/config/gunicorn.py
