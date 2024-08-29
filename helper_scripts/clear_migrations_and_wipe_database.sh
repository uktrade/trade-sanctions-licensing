#!/bin/bash

# rebuilds migration files, wipes the database, and runs migrations

cd ".." || exit
rm django_app/apply_for_a_licence/migrations/*.py
rm django_app/view_a_licence/migrations/*.py

touch django_app/apply_for_a_licence/migrations/__init__.py
touch django_app/view_a_licence/migrations/__init__.py

pipenv run python django_app/manage.py makemigrations

rm -r pgdata
docker-compose down
docker-compose up -d
sleep 35
pipenv run python django_app/manage.py migrate
