"""
Django's settings for backend project.

Generated by 'django-admin startproject' using Django 4.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

dotenv_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY: str = os.environ.get('SECRET_KEY', '')

API_PREFIX = 'api/v1/'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'django_extensions',
    'api.apps.ApiConfig',
    'drf_spectacular',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASE_HOST: str = os.environ.get('DATABASE_HOST', '127.0.0.1')
DATABASE_PORT: str = os.environ.get('DATABASE_PORT', '5432')
DATABASE_NAME: str = os.environ.get('DATABASE_NAME', 'semd')
DATABASE_USER: str = os.environ.get('DATABASE_USER', 'semd')
DATABASE_PASSWORD: str = os.environ.get('DATABASE_PASSWORD', '')

EGISZ_DB_HOST: str = os.environ.get('EGISZ_DB_HOST', '127.0.0.1')
EGISZ_DB_PORT: str = os.environ.get('EGISZ_DB_PORT', '5432')
EGISZ_DB_NAME: str = os.environ.get('EGISZ_DB_NAME', 'egisz-db')
EGISZ_DB_USER: str = os.environ.get('EGISZ_DB_USER', 'semd')
EGISZ_DB_PASSWORD: str = os.environ.get('EGISZ_DB_PASSWORD', '')

ONCOR_DATA_ANALYTICS_HOST: str = os.environ.get('ONCOR_DATA_ANALYTICS_HOST', '127.0.0.1')
ONCOR_DATA_ANALYTICS_PORT: str = os.environ.get('ONCOR_DATA_ANALYTICS_PORT', '5432')
ONCOR_DATA_ANALYTICS_NAME: str = os.environ.get('ONCOR_DATA_ANALYTICS_NAME', 'oncor-data-analytics')
ONCOR_DATA_ANALYTICS_USER: str = os.environ.get('ONCOR_DATA_ANALYTICS_USER', 'semd')
ONCOR_DATA_ANALYTICS_PASSWORD: str = os.environ.get('ONCOR_DATA_ANALYTICS_PASSWORD', '')

ROSMINZDRAV_DIRECTORIES_HOST: str = os.environ.get('ROSMINZDRAV_DIRECTORIES_HOST', '127.0.0.1')
ROSMINZDRAV_DIRECTORIES_PORT: str = os.environ.get('ROSMINZDRAV_DIRECTORIES_PORT', '5432')
ROSMINZDRAV_DIRECTORIES_NAME: str = os.environ.get('ROSMINZDRAV_DIRECTORIES_NAME', 'rosminzdrav-directories')
ROSMINZDRAV_DIRECTORIES_USER: str = os.environ.get('ROSMINZDRAV_DIRECTORIES_USER', 'semd')
ROSMINZDRAV_DIRECTORIES_PASSWORD: str = os.environ.get('ROSMINZDRAV_DIRECTORIES_PASSWORD', '')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_HOST,
        'PORT': DATABASE_PORT,
    },
    'egisz-db': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': EGISZ_DB_NAME,
        'USER': EGISZ_DB_USER,
        'PASSWORD': EGISZ_DB_PASSWORD,
        'HOST': EGISZ_DB_HOST,
        'PORT': EGISZ_DB_PORT,
    },
    'oncor-data-analytics': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': ONCOR_DATA_ANALYTICS_NAME,
        'USER': ONCOR_DATA_ANALYTICS_USER,
        'PASSWORD': ONCOR_DATA_ANALYTICS_PASSWORD,
        'HOST': ONCOR_DATA_ANALYTICS_HOST,
        'PORT': ONCOR_DATA_ANALYTICS_PORT,
    },
    'rosminzdrav-directories': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': ROSMINZDRAV_DIRECTORIES_NAME,
        'USER': ROSMINZDRAV_DIRECTORIES_USER,
        'PASSWORD': ROSMINZDRAV_DIRECTORIES_PASSWORD,
        'HOST': ROSMINZDRAV_DIRECTORIES_HOST,
        'PORT': ROSMINZDRAV_DIRECTORIES_PORT,
    },
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = "/api/v1/signin"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(seconds=int(os.environ.get('ACCESS_TOKEN_LIFETIME', 60 * 60 * 24))),
    "REFRESH_TOKEN_LIFETIME": timedelta(seconds=int(os.environ.get('REFRESH_TOKEN_LIFETIME', 60 * 60 * 24 * 30))),
}

CORS_ORIGIN_WHITELIST = ["http://localhost:3000", "http://127.0.0.1:3000"]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],

    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    'DEFAULT_PAGINATION_CLASS': 'api.pagination.pagination.SemdPageNumberPagination',
    'PAGE_SIZE': int(os.environ.get('PAGE_SIZE', 10)),

    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),

    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    'DEFAULT_METADATA_CLASS': 'rest_framework.metadata.SimpleMetadata',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'ONCOR SEMD API',
    'DESCRIPTION': '''
    ONCOR Prototypes REST API
    All API requests must be authorized using the Bearer token authorization
    The token is obtained upon authorization using the /api/user/login method
    ''',
    'VERSION': '0.0.1',
    'SERVE_INCLUDE_SCHEMA': False,
}
