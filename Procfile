web: python django_app/manage.py migrate && python django_app/manage.py collectstatic --no-input && gunicorn django_app.config.wsgi --config django_app/config/gunicorn.py
