"""
Django settings for incentive_system project.
"""

from pathlib import Path
from decouple import config, Csv
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_bootstrap5',
    'accounts',
    'points',
    'products',
    'transactions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'incentive_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'incentive_system.context_processors.company_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'incentive_system.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
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
LANGUAGE_CODE = 'ja'
TIME_ZONE = 'Asia/Tokyo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Bootstrap5 settings - simplified
BOOTSTRAP5 = {}

# ホワイトレーベル設定
COMPANY_SETTINGS = {
    'COMPANY_NAME': config('COMPANY_NAME', default='ABC商事株式会社'),
    'SYSTEM_NAME': config('SYSTEM_NAME', default='営業成果インセンティブシステム'),
    'SYSTEM_SHORT_NAME': config('SYSTEM_SHORT_NAME', default='ABC インセンティブ'),
    'COMPANY_LOGO_URL': config('COMPANY_LOGO_URL', default='https://via.placeholder.com/200x40/2c5282/ffffff?text=ABC%E5%95%86%E4%BA%8B'),
    'COMPANY_COLOR_PRIMARY': config('COMPANY_COLOR_PRIMARY', default='#2c5282'),
    'COMPANY_COLOR_SECONDARY': config('COMPANY_COLOR_SECONDARY', default='#4a5568'),
    'COMPANY_URL': config('COMPANY_URL', default='https://abc-trading.example.com'),
    'SUPPORT_EMAIL': config('SUPPORT_EMAIL', default='support@abc-trading.example.com'),
    'COPYRIGHT_TEXT': config('COPYRIGHT_TEXT', default='© 2024 ABC商事株式会社. All rights reserved.'),
}
