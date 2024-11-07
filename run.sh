#!/bin/bash -e

# install wkhtmltopdf and it's dependencies
echo "Installing wkhtmltopdf"
apt-get update && apt-get install -y \
  wget \
  xfonts-75dpi \
  fontconfig \
  libxrender1 \
  libxexr6 \
  ca-certificates

wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.0g-2ubuntu4_amd64.deb
dpkg -i ./libssl1.1_1.1.0g-2ubuntu4_amd64.deb
rm libssl1.1_1.1.0g-2ubuntu4_amd64.deb

wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.bionic_amd64.deb
apt install -y ./wkhtmltox_0.12.6-1.bionic_amd64.deb

echo "Running migrations"
python django_app/manage.py migrate
python django_app/manage.py collectstatic --no-input

# Start webserver
echo "Running in DBT Platform"
gunicorn django_app.config.wsgi --config django_app/config/gunicorn.py
