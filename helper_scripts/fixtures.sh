#!/bin/bash
# Load all fixtures in one go

echo "Loading all fixture data"


cd ".." || exit
cd "django_app" || exit
pipenv run python manage.py loaddata apply_for_a_licence/fixtures/*.json

echo "Fixtures loaded"
