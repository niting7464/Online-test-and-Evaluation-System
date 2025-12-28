import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import dj_database_url

# Deployment Test - Version 1.0

# ----------------------------
# BASE DIRECTORY
# ----------------------------
# For: mindsprint/mindsprint/settings.py
# .parent.parent points to the root 'mindsprint' folder (containing manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------
# LOAD ENVIRONMENT VARIABLES
# ----------------------------
# Ensure .env is loaded before any variables are used
load_dotenv(os.path.join(BASE_DIR, ".env"))

# ----------------------------
# SECURITY
# ----------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".onrender.com", 
    "https://online-test-and-evaluation-system-1.onrender.com/"
]


# ----------------------------
# APPLICATIONS
# ----------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_extensions',

    'accounts',
    'tests',
]

# ----------------------------
# MIDDLEWARE
# ----------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise must be here
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.SessionUserMiddleware',
]

ROOT_URLCONF = 'mindsprint.urls'

# ----------------------------
# TEMPLATES
# ----------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.current_user',
            ],
        },
    },
]

WSGI_APPLICATION = 'mindsprint.wsgi.application'

# ----------------------------
# DATABASE
# ----------------------------
import dj_database_url
import os

# ... rest of settings ...
# --- Find your DATABASE section and replace it with this ---

# 1. Define a fallback (local)
# ----------------------------
# DATABASE CONFIGURATION
# ----------------------------
# Check if we are running on Render
ON_RENDER = 'RENDER' in os.environ

if ON_RENDER:
    # Use the Render Internal Database URL
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    # Local Development (your laptop)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "mindsprint_db",
            "USER": "postgres",
            "PASSWORD": "0000",
            "HOST": "localhost",
            "PORT": "5432",
        }
    }
# ----------------------------
# STATIC & MEDIA FILES (Fixed & Consolidated)
# ----------------------------
STATIC_URL = "/static/"

# This is where collectstatic will gather files (Absolute Path)
# Use BASE_DIR so paths remain portable across environments
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Storage engine for WhiteNoise — use compressed manifest for production caching
# If you prefer Django 4.2+ STORAGES setting, convert accordingly.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# ----------------------------
# REST FRAMEWORK & JWT
# ----------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ----------------------------
# ADDITIONAL CONFIG
# ----------------------------
AUTH_USER_MODEL = 'accounts.User'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Email
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
BREVO_API_KEY = os.getenv("BREVO_API_KEY")

PASSWORD_RESET_DOMAIN = os.getenv(
    "PASSWORD_RESET_DOMAIN",
    "http://localhost:8000"
)


LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/login/"
LOGIN_URL = "/login/"


db_from_env = dj_database_url.config(conn_max_age=600)
DATABASES['default'].update(db_from_env)

# This print will show up in your Render Logs to help us debug
if os.getenv('DATABASE_URL'):
    print("✅ DATABASE_URL found in environment")
else:
    print("❌ DATABASE_URL NOT FOUND - Check Render Dashboard")





