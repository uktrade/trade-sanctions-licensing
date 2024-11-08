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
yum install -y \
  fontconfig
  freetype
  freetype=deve;
  libX11
  libXext
  libextrender
  xorg-x11-fonts-Type1
  xorg-x11-fonts-75dpi
  wget

#wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.0g-2ubuntu4_amd64.deb
#sudo apt install ./libssl1.1_1.1.0g-2ubuntu4_amd64.deb
#rm libssl1.1_1.1.0g-2ubuntu4_amd64.deb

wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.amazonlinux2.x86_64.rpm
#wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6/wkhtmltox_0.12.6-1.centos7.x86_64.rpm
yum localinstall -y wkhtmltox-0.12.6-1.amazonlinux2.x86_64.rpm
rm wkhtmltox-0.12.6-1.amazonlinux2.x86_64.rpm

echo "Running django_app/manage.py collectstatic --noinput"
python django_app/manage.py collectstatic --no-input
