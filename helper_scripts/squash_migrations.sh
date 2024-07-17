#!/bin/bash

cd ".." || exit
cd "django_app" || exit
rm apply_for_a_licence/migrations/*.py
touch apply_for_a_licence/migrations/__init__.py
pipenv run python manage.py makemigrations
