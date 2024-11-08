#!/usr/bin/env bash
# Exit early if something goes wrong
set -e

# Add commands below to run inside the container after all the other buildpacks have been applied
export BUILD_STEP='True'
export COPILOT_ENVIRONMENT_NAME='build'
export DJANGO_SECRET_KEY='dummy_key'
export DEBUG='True'
export DATABASE_CREDENTIALS='{"username": "postgres", "password": "password", "engine": "postgres", "port": 5432, "dbname": "postgres", "host": "db", "dbInstanceIdentifier": "emt-db"}'
export DJANGO_SETTINGS_MODULE='config.settings.deploy.development'

echo "Installing wkhtmltopdf"
sudo apt-get update && apt-get install -y \
  wget \
  xfonts-75dpi \
  fontconfig \
  libxrender1 \
  libxexr6 \
  ca-certificates

wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.0g-2ubuntu4_amd64.deb
sudo apt install ./libssl1.1_1.1.0g-2ubuntu4_amd64.deb
rm libssl1.1_1.1.0g-2ubuntu4_amd64.deb

wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.bionic_amd64.deb
sudo apt install ./wkhtmltox_0.12.6-1.bionic_amd64.deb

echo "Running django_app/manage.py collectstatic --noinput"
python django_app/manage.py collectstatic --no-input
