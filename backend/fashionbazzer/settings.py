"""
Django settings for fashionbazzer project.

Generated for FashionBazzer - Affiliate Marketing Automation Engine.
"""

import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ── Helpers for env var parsing ──
def _parse_bool(value):
    """Parse a string/env-var into a boolean.
    'true', '1', 'yes' → True (case-insensitive).
    Everything else → False.
    Using cast=bool directly would be wrong since bool('false') == True.
    """
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ('true', '1', 'yes')

def _parse_list(value):
    if not value:
        return []
    return [item.strip() for item in value.split(',') if item.strip()]


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=_parse_bool)

ALLOWED_HOSTS = _parse_list(config('ALLOWED_HOSTS', default='localhost,127.0.0.1'))

# Trust Render default host name if running in production on Render
RENDER_EXTERNAL_HOSTNAME = config('RENDER_EXTERNAL_HOSTNAME', default='')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'corsheaders',
    'django_apscheduler',
    # Local apps
    'apps.products',
    'apps.content',
    'apps.poster',
    'apps.tracker',
    'apps.dashboard',
    'apps.marketing',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fashionbazzer.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'fashionbazzer.wsgi.application'
ASGI_APPLICATION = 'fashionbazzer.asgi.application'

# ── Security Settings (production only) ──
if not DEBUG:
    # Redirect all HTTP to HTTPS
    SECURE_SSL_REDIRECT = True
    # Render uses proxy headers — trust them for HTTPS detection
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    # Use secure cookies (HTTPS only)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # HTTP Strict Transport Security (1 year)
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    # Prevent clickjacking
    X_FRAME_OPTIONS = 'DENY'

# Database
# Use PostgreSQL in production, SQLite for local development
DATABASE_URL = config('DATABASE_URL', default='')
if DATABASE_URL:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS Configuration
CORS_ALLOWED_ORIGINS = _parse_list(config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://localhost:8000'
))

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# APScheduler Configuration
APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"
SCHEDULER_AUTOSTART = True

# ──────────────────────────────────────────
# External Service API Keys (from env)
# ──────────────────────────────────────────

# Affiliate
AMAZON_ASSOCIATE_ID = config('AMAZON_ASSOCIATE_ID', default='')
MEESHO_AFFILIATE_ID = config('MEESHO_AFFILIATE_ID', default='')
CUELINKS_ID = config('CUELINKS_ID', default='')

# Telegram
TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN', default='')
TELEGRAM_CHANNEL_ID = config('TELEGRAM_CHANNEL_ID', default='')

# Meta (Instagram + Facebook)
META_ACCESS_TOKEN = config('META_ACCESS_TOKEN', default='')
META_USER_ID = config('META_USER_ID', default='')
FB_PAGE_ID = config('FB_PAGE_ID', default='')
FB_PAGE_ACCESS_TOKEN = config('FB_PAGE_ACCESS_TOKEN', default='')
INSTAGRAM_USER_ID = config('INSTAGRAM_USER_ID', default='')

# Pinterest
PINTEREST_ACCESS_TOKEN = config('PINTEREST_ACCESS_TOKEN', default='')
PINTEREST_BOARD_ID = config('PINTEREST_BOARD_ID', default='')
PINTEREST_BOARD_NAME = config('PINTEREST_BOARD_NAME', default='fashion-brazzer')

# Twitter/X
TWITTER_API_KEY = config('TWITTER_API_KEY', default='')
TWITTER_API_SECRET = config('TWITTER_API_SECRET', default='')
TWITTER_ACCESS_TOKEN = config('TWITTER_ACCESS_TOKEN', default='')
TWITTER_ACCESS_SECRET = config('TWITTER_ACCESS_SECRET', default='')

# AI
HUGGINGFACE_API_KEY = config('HUGGINGFACE_API_KEY', default='')

# Cloudinary (for public image URLs)
CLOUDINARY_URL = config('CLOUDINARY_URL', default='')

# remove.bg
REMOVEBG_API_KEY = config('REMOVEBG_API_KEY', default='')

# Redirect base URL for tracked links
REDIRECT_BASE_URL = config('REDIRECT_BASE_URL', default='http://localhost:8000/r/')
