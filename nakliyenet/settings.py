"""
Django settings for nakliyenet project.
"""

import os
from pathlib import Path
from decouple import config
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',

    # Third party
    'rest_framework',
    'django_filters',
    'corsheaders',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # Local apps
    'website',
    'blog',
]

# Site ID for django-allauth
SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS for API
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'nakliyenet.urls'

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
                'website.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'nakliyenet.wsgi.application'

# Database - SQLite for local development, PostgreSQL for production
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=BASE_DIR / 'db.sqlite3'),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
    }
}

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Django default
    'allauth.account.auth_backends.AuthenticationBackend',  # django-allauth (Google OAuth)
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# django-allauth configuration
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_SIGNUP_REDIRECT_URL = '/profilim/'

# Social account providers (Google OAuth)
# NOTE: Using database-backed SocialApp (configured in Django admin)
# DO NOT configure 'APP' here to avoid MultipleObjectsReturned error
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

# Google OAuth settings
SOCIALACCOUNT_AUTO_SIGNUP = True  # Automatically create account on first Google login
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'  # Skip email verification for social accounts
SOCIALACCOUNT_LOGIN_ON_GET = True  # Skip confirmation page, login directly!

# Force HTTPS for OAuth redirect URIs (required for production OAuth apps)
# Use 'http' for local development, 'https' for production
ACCOUNT_DEFAULT_HTTP_PROTOCOL = config('ACCOUNT_DEFAULT_HTTP_PROTOCOL', default='http')

# Login/Logout URLs
LOGIN_URL = '/giris/'
LOGOUT_URL = '/cikis/'

# Internationalization
LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# WhiteNoise cache optimization (1 year cache for static files)
WHITENOISE_MAX_AGE = 31536000  # 1 year in seconds

# Immutable files (with content hash in filename) get forever cache
WHITENOISE_IMMUTABLE_FILE_TEST = lambda path, url: True

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings (mobil app için API çağrıları)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
]

# Site settings
SITE_URL = config('SITE_URL', default='http://localhost:8000')
IOS_APP_URL = config('IOS_APP_URL', default='https://apps.apple.com/app/nakliyenet')
ANDROID_APP_URL = config('ANDROID_APP_URL', default='https://play.google.com/store/apps/details?id=com.nakliyenet.app')

# Email settings
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # Production email settings (örnek SMTP)
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@nakliyenet.com')

# Security settings for production
# Tell Django to trust X-Forwarded-Proto header from nginx
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Read from environment for flexibility
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default='True', cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default='True', cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default='True', cast=bool)
SECURE_BROWSER_XSS_FILTER = config('SECURE_BROWSER_XSS_FILTER', default='True', cast=bool)
SECURE_CONTENT_TYPE_NOSNIFF = config('SECURE_CONTENT_TYPE_NOSNIFF', default='True', cast=bool)
X_FRAME_OPTIONS = config('X_FRAME_OPTIONS', default='DENY')

# Additional security headers
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CSRF Trusted Origins for HTTPS
CSRF_TRUSTED_ORIGINS = [
    'https://nakliyenet.com',
    'https://www.nakliyenet.com',
]

# Django REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# ==============================
# Sentry Configuration - Error Tracking & Performance Monitoring
# ==============================
SENTRY_DSN = config('SENTRY_DSN', default='')

if SENTRY_DSN and not DEBUG:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
        ],
        # Performance Monitoring
        traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
        
        # Error Sampling
        sample_rate=1.0,  # 100% error sampling
        
        # Send user context
        send_default_pii=False,  # GDPR compliance - don't send PII
        
        # Environment
        environment=config('SENTRY_ENVIRONMENT', default='production'),
        
        # Release tracking
        release=config('SENTRY_RELEASE', default='1.0.0'),
        
        # Additional options
        attach_stacktrace=True,
        max_breadcrumbs=50,
        
        # Before send hook - customize what gets sent
        before_send=lambda event, hint: event if not DEBUG else None,
    )
    
    print(f"[OK] Sentry initialized - Environment: {config('SENTRY_ENVIRONMENT', default='production')}")
elif DEBUG:
    print("[INFO] Sentry disabled in DEBUG mode")
else:
    print("[WARN] Sentry DSN not configured")
