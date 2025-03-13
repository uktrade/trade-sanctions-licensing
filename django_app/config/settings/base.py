"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path

import dj_database_url
import sentry_sdk
from authentication.config import OneLoginConfig
from config.env import env
from django.conf.locale.en import formats as en_formats
from django.urls import reverse_lazy
from sentry_sdk.integrations.django import DjangoIntegration

is_dbt_platform = "COPILOT_ENVIRONMENT_NAME" in os.environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # django_app/
ROOT_DIR = BASE_DIR.parent  # licensing/

SECRET_KEY = env.django_secret_key

DEBUG = env.debug
INCLUDE_PRIVATE_URLS = env.include_private_urls
SHOW_ADMIN_PANEL = DEBUG and INCLUDE_PRIVATE_URLS

ALLOWED_HOSTS = env.allowed_hosts

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

OUR_APPS = ["config", "core", "authentication", "healthcheck", "feedback", "apply_for_a_licence", "view_a_licence"]

THIRD_PARTY_APPS = [
    "crispy_forms",
    "crispy_forms_gds",
    "django_chunk_upload_handlers",
    "simple_history",
    "storages",
    "authbroker_client",
    "django_countries",
]

INSTALLED_APPS = DJANGO_APPS + OUR_APPS + THIRD_PARTY_APPS

CRISPY_ALLOWED_TEMPLATE_PACKS = ("bootstrap", "bootstrap3", "bootstrap4", "uni_form", "gds")
CRISPY_TEMPLATE_PACK = "gds"

# AWS
AWS_S3_REGION_NAME = env.aws_default_region
AWS_ENDPOINT_URL = env.aws_endpoint_url

# General S3
AWS_S3_OBJECT_PARAMETERS = {"ContentDisposition": "attachment"}
PRESIGNED_URL_EXPIRY_SECONDS = env.presigned_url_expiry_seconds
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_DEFAULT_ACL = "private"

# Temporary document bucket
TEMPORARY_S3_BUCKET_ACCESS_KEY_ID = env.temporary_s3_bucket_configuration["access_key_id"]
TEMPORARY_S3_BUCKET_SECRET_ACCESS_KEY = env.temporary_s3_bucket_configuration["secret_access_key"]
TEMPORARY_S3_BUCKET_NAME = env.temporary_s3_bucket_configuration["bucket_name"]

# Permanent document bucket
PERMANENT_S3_BUCKET_ACCESS_KEY_ID = env.permanent_s3_bucket_configuration["access_key_id"]
PERMANENT_S3_BUCKET_SECRET_ACCESS_KEY = env.permanent_s3_bucket_configuration["secret_access_key"]
PERMANENT_S3_BUCKET_NAME = env.permanent_s3_bucket_configuration["bucket_name"]

# S3FileUploadHandler
AWS_ACCESS_KEY_ID = TEMPORARY_S3_BUCKET_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = TEMPORARY_S3_BUCKET_SECRET_ACCESS_KEY
AWS_REGION = AWS_S3_REGION_NAME
AWS_STORAGE_BUCKET_NAME = TEMPORARY_S3_BUCKET_NAME  # where files are uploaded as part of django_chunk_upload_handlers

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = ROOT_DIR / "static"

# Media Files Storage
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {"bucket_name": env.temporary_s3_bucket_configuration["bucket_name"]},
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# File storage
FILE_UPLOAD_HANDLERS = (
    "django_chunk_upload_handlers.clam_av.ClamAVFileUploadHandler",
    "core.custom_upload_handler.CustomFileUploadHandler",
)  # Order is important

# CLAM AV
CLAM_AV_USERNAME = env.clam_av_username
CLAM_AV_PASSWORD = env.clam_av_password
CLAM_AV_DOMAIN = env.clam_av_domain
CHUNK_UPLOADER_RAISE_EXCEPTION_ON_VIRUS_FOUND = False

# MIDDLEWARE
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django_permissions_policy.PermissionsPolicyMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "core.middleware.CurrentSiteMiddleware",
    "django_ratelimit.middleware.RatelimitMiddleware",
    "csp.middleware.CSPMiddleware",
    "core.middleware.SetPermittedCrossDomainPolicyHeaderMiddleware",
    "core.middleware.CacheControlMiddleware",
    "core.middleware.XSSProtectionMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "core.sites.context_processors.sites",
                "core.context_processors.truncate_words_limit",
                "core.context_processors.is_debug_mode",
                "core.context_processors.back_button",
                "core.context_processors.session_expiry_times",
                "core.context_processors.sentry_configuration_options",
                "core.context_processors.environment_information",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
DATABASES = {
    "default": {
        **dj_database_url.parse(
            env.database_uri,
            engine="postgresql",
            conn_max_age=0,
        ),
        "ENGINE": "django.db.backends.postgresql",
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# COMPANIES HOUSE API
COMPANIES_HOUSE_API_KEY = env.companies_house_api_key

# GOV NOTIFY
GOV_NOTIFY_API_KEY = env.gov_notify_api_key
EMAIL_VERIFY_CODE_TEMPLATE_ID = env.email_verify_code_template_id
NEW_OTSI_USER_TEMPLATE_ID = env.new_otsi_user_template_id
PUBLIC_USER_NEW_APPLICATION_TEMPLATE_ID = env.public_user_new_application_template_id
OTSI_NEW_APPLICATION_TEMPLATE_ID = env.otsi_new_application_template_id
DELETE_LICENCE_APPLICATION_TEMPLATE_ID = env.delete_licence_application_template_id
if "," in env.new_application_alert_recipients:  # check if multiple recipients
    NEW_APPLICATION_ALERT_RECIPIENTS = env.new_application_alert_recipients.split(",")
else:
    NEW_APPLICATION_ALERT_RECIPIENTS = [env.new_application_alert_recipients]

# SENTRY
SENTRY_DSN = env.sentry_dsn
SENTRY_ENVIRONMENT = env.sentry_environment
SENTRY_ENABLE_TRACING = env.sentry_enable_tracing
SENTRY_TRACES_SAMPLE_RATE = env.sentry_traces_sample_rate
SENTRY_ENABLED = SENTRY_DSN and SENTRY_ENVIRONMENT

if SENTRY_ENABLED:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=SENTRY_ENVIRONMENT,
        integrations=[DjangoIntegration()],
        enable_tracing=SENTRY_ENABLE_TRACING,
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
    )

# Email Verification settings
EMAIL_VERIFY_TIMEOUT_SECONDS = env.email_verify_timeout_seconds

# Google Analytics
GTM_ENABLED = env.gtm_enabled
GTM_ID = env.gtm_id

# Authentication
AUTHENTICATION_BACKENDS = [
    "authentication.backends.StaffSSOBackend",
    "authentication.backends.OneLoginBackend",
]

if SHOW_ADMIN_PANEL:
    AUTHENTICATION_BACKENDS.insert(0, "authentication.backends.AdminBackend")

# Staff SSO
AUTHBROKER_URL = env.authbroker_url
AUTHBROKER_CLIENT_ID = env.authbroker_client_id
AUTHBROKER_CLIENT_SECRET = env.authbroker_client_secret
AUTHBROKER_TOKEN_SESSION_KEY = env.authbroker_token_session_key
AUTHBROKER_STAFF_SSO_SCOPE = env.authbroker_staff_sso_scope

# GOV.UK One Login
GOV_UK_ONE_LOGIN_CLIENT_ID = env.gov_uk_one_login_client_id
GOV_UK_ONE_LOGIN_CLIENT_SECRET = env.gov_uk_one_login_client_secret
GOV_UK_ONE_LOGIN_CONFIG = OneLoginConfig
GOV_UK_ONE_LOGIN_ENABLED = False

LOGIN_REDIRECT_URL = reverse_lazy("initial_redirect_view")
PUBLIC_USER_GROUP_NAME = "public_users"
INTERNAL_USER_GROUP_NAME = "internal_users"
ADMIN_USER_GROUP_NAME = "admin_users"

TRUNCATE_WORDS_LIMIT = 30

en_formats.DATE_FORMAT = "d/m/Y"

# Django sites
APPLY_FOR_A_LICENCE_DOMAIN = env.apply_for_a_licence_domain
VIEW_A_LICENCE_DOMAIN = env.view_a_licence_domain
PROTOCOL = "https://"

# Django Ratelimit
RATELIMIT_VIEW = "core.views.base_views.rate_limited_view"
RATELIMIT = "10/m"

# Redis
REDIS_URL = env.redis_url

# Caches
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "TIMEOUT": 60 * 60 * 24,  # in seconds: 60 * 60 * 24 (24 hours)
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
#
# TODO: For save-and-return testing only, revert to 40 minutes BEFORE merge to main
#

SESSION_COOKIE_AGE = 6 * 60
SESSION_LAST_ACTIVITY_KEY = "last_form_submission"

# CSP policies

# The default policy is to only allow resources from the same origin (self)
CSP_DEFAULT_SRC = ("'self'",)

# JS tags with a src attribute can only be loaded from report-a-suspected-breach and other trusted sources
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-eval'",
    "https://sentry.ci.uktrade.digital/",
    "https://cdnjs.cloudflare.com",
    "https://www.googletagmanager.com",
    "https://*.google-analytics.com",
    "https://browser.sentry-cdn.com",
    "https://raven.ci.uktrade.io",
)

# JS scripts can import other scripts, following the same rules as above
CSP_CONNECT_SRC = CSP_SCRIPT_SRC

# CSS elements with a src attribute can only be loaded from report-a-suspected-breach itself,
# inline, e.g. <style> tags, or from Cloudflare
CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",
    "https://cdnjs.cloudflare.com",
)
# Images can only be loaded from report-a-suspected-breach itself, data URIs, and Cloudflare
CSP_FONT_SRC = (
    "'self'",
    "data:",
    "https://cdnjs.cloudflare.com",
)
# Images can only be loaded from report-a-suspected-breach itself, data URIs, and Google Tag Manager
CSP_IMG_SRC = (
    "'self'",
    "data:",
    "https://www.googletagmanager.com",
)

# CSP meta-settings

# inline scripts without a src attribute must have a nonce attribute
CSP_INCLUDE_NONCE_IN = ["script-src"]

# if True, CSP violations are reported but not enforced
CSP_REPORT_ONLY = env.csp_report_only

# URL to send CSP violation reports to
# CSP_REPORT_URI = env.csp_report_uri

# Permissions policy header
PERMISSIONS_POLICY = {
    "fullscreen": ["self"],
    "accelerometer": [],
    "ambient-light-sensor": [],
    "autoplay": [],
    "camera": [],
    "display-capture": [],
    "document-domain": [],
    "encrypted-media": [],
    "geolocation": [],
    "gyroscope": [],
    "interest-cohort": [],
    "magnetometer": [],
    "microphone": [],
    "midi": [],
    "payment": [],
    "usb": [],
}
SESSION_COOKIE_HTTPONLY = True

# Information about the current environment
CURRENT_BRANCH = env.current_branch
CURRENT_TAG = env.current_tag
CURRENT_COMMIT = env.current_commit

# Save & Return
DRAFT_APPLICATION_EXPIRY_DAYS = 28  # the number of days a draft application is valid for
