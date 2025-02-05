#!/bin/bash

echo "$COPILOT_ENVIRONMENT_NAME"

if [[ "$COPILOT_ENVIRONMENT_NAME" == "dev" ]]
then
  echo "Tearing down DB"
  python django_app/manage.py drop_all_tables
fi

echo "Running migrations"
python django_app/manage.py migrate && python django_app/manage.py collectstatic --no-input && gunicorn django_app.config.wsgi --config django_app/config/gunicorn.py
