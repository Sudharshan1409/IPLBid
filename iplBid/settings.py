"""
Django settings for iplBid project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import os
import json

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
creds_file = open(os.path.join(BASE_DIR, 'creds.json'), 'r')
creds = json.load(creds_file)
creds_file.close()

TEAM_COLOR_CODES = {
    'MI': '#004ba0',
    'KKR': '#2e0854',
    'RCB': '#ec1c23',
    'CSK': '#ffff3c',
    'RR': '#254aa5',
    'KXIP': '#ed1b24',
    'DD': '#0000b8',
    'SRH': '#ff822a',
    'GT': '#f9f9f9',
    'LSG': '#50cdc3',
}
CURRENT_YEAR = 2024
os.environ['CURRENT_YEAR'] = str(CURRENT_YEAR)

ALL_TEAMS = [
    'DC',
    'PBKS',
    'KKR',
    'LSG',
    'SRH',
    'RR',
    'GT',
    'CSK',
    'RCB',
    'MI',
]

IPL_TEAMS = []

for team in ALL_TEAMS:
    IPL_TEAMS.append((team, team))

DREAM11_PLAYERS = [
    ('Darshan', 'Darshan'),
    ('Panee', 'Panee'),
    ('Badri', 'Badri'),
    ('Srinidhi', 'Srinidhi'),
    # ('Nandan', 'Nandan'),
    ('PavanG', 'PavanG'),
    ('PavanK', 'PavanK'),
    ('Ananthu', 'Ananthu'),
    ('Teju', 'Teju'),
    ('Jithu', 'Jithu'),
]

DREAM11_PLAYERS_USERNAMES = [
    'paneendragautham',
    'bprasadv',
    'Pavangautham@17',
    'AnanthaM_95',
    'Jagaluru_boys',
    'txms',
    'Jithu'
]

PRICE_VALUES = {
    1: 45,
    2: 30,
    3: 15,
}


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-3i((eps*(0y%&df@8jiy&tu4wxt)2ny33$0_lqgcb_kf#7-elx'

# SECURITY WARNING: don't run with debug turned on in production!
if creds['debug']:
    DEBUG = True
else:
    DEBUG = False

MINIMUM_BID_VALUE = 500
MAXIMUM_BID_VALUE = 3000

PLAYOFFS_MINIMUM_BID_VALUE = 1000
PLAYOFFS_MAXIMUM_BID_VALUE = 5000

ALLOWED_HOSTS = ["*"]

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

CRONJOBS = [
    ('0 14,18 * * *', 'bid.views.remainder', f">> {os.path.join(BASE_DIR, 'remainder.log')}"),
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap5',
    'django_crontab',
    'bid',
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

ROOT_URLCONF = 'iplBid.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
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

WSGI_APPLICATION = 'iplBid.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = creds['email']
EMAIL_HOST_PASSWORD = creds['password']
SECRET_KEY = creds['secret_key']

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
LOGOUT_REDIRECT_URL = '/'

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
