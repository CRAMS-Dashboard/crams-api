"""
Django settings for crams_collection project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import importlib
import logging
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'vix)4vqajw@i5=2ed0&3_7nq6zw#x5fl*&0sezzjbw148j%9-z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1']

NECTAR_NOTIFICATION_REPLY_TO = "email@me"
CRAMS_APP_CONFIG_LIST = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_extensions',
    'django_filters',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'merc_common',
    'crams',
    'crams_log',
    'crams_notification',
    'crams_contact',
    'crams_manager',
    'crams_collection',
    'crams_compute',
    'crams_storage',
    'crams_allocation',
    'crams_provision',
    'crams_member',
    'crams_resource_usage',
    'crams_resource_usage.storage',
    'crams_resource_usage.compute',
    'crams_reports',
    'crams_racmon',
    'crams_api'
]

AUTH_USER_MODEL = 'crams.User'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# allow the cors origin
CORS_ORIGIN_ALLOW_ALL = True
# append the back slash
APPEND_SLASH = True

ROOT_URLCONF = 'crams_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'loaders': [
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
WSGI_APPLICATION = 'crams_allocation.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# API module Integration
CRAMS_ASPECT_CONFIG_LIST = [
    # erb System configs
    'crams_racmon.config.config_init',
    # Aspect config
    'crams_collection.config.aspect_config',
    'crams_allocation.config.aspect_config',
    'crams_member.config.aspect_config',
    'crams_racmon.config.aspect_config',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'crams_contact.auth.crams_token_auth.CramsTokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'crams.utils.rest_utils.BrowsableAPIRendererWithoutForms',
    ),
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Run environment settings
DEV_ENVIRONMENT = 'development'
STAGING_ENVIRONMENT = 'staging'
QAT_ENVIRONMENT = 'qat'
PROD_ENVIRONMENT = 'production'
CURRENT_RUN_ENVIRONMENT = DEV_ENVIRONMENT

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-au'
TIME_ZONE = 'Australia/Melbourne'
USE_I18N = True
USE_L10N = True
USE_TZ = True
import logging

# Celery broker configuration for Rabbit MQ
CELERY_BROKER_URL = 'amqp://mq_admin:mq_admin_pwd@mq_ip_address:5672/crams_opensource'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
# ref to http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html#crontab-schedules
# CELERY Cron Job
CELERY_BEAT_SCHEDULE = {}
# end of Celery Configuration

# Enable Rabbit MQ to send email, default is False
MQ_MAIL_ENABLED = False
# Send email to the console by default
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# Or have an smtp backend, it will send email to admin user
EMAIL_HOST = 'smtp.crams.com'
MAILER_EMAIL_BACKEND = EMAIL_BACKEND
EMAIL_SENDER = 'sender@crams.com'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'), ]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

DEFAULT_CLIENT_VIEW_REQUEST_PATH = '/#/allocations/view_request/'
DEFAULT_CLIENT_VIEW_APPROVAL_PATH = '/#/approval/view_request/'

RACMON_CLIENT_BASE_URL = 'https://127.0.0.1'
RACMON_CLIENT_VIEW_REQUEST_PATH = DEFAULT_CLIENT_VIEW_REQUEST_PATH
RACMON_CLIENT_VIEW_APPROVAL_PATH = DEFAULT_CLIENT_VIEW_APPROVAL_PATH
RACMON_CLIENT_VIEW_JOIN_PATH = '/#/allocations/join_project/'
RACMON_CLIENT_VIEW_MEMBER_PATH = '/#/allocations/membership/'

# Import the local_settings.py to override some of the default settings,
# like database settings
try:
    from crams_api.local.local_settings import *
except ImportError:
    logging.debug("No local_settings file found.")

# override the celery settings
try:
    from crams_api.local.celery_settings import *
except ImportError:
    logging.debug("No celery_settings file found.")
