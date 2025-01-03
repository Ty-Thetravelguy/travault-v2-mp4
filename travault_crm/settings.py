from pathlib import Path
import os
from dotenv import load_dotenv
from storages.backends.s3boto3 import S3Boto3Storage

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file in project root
ENV_FILE = BASE_DIR / '.env'
load_dotenv(ENV_FILE)

# Stripe API keys
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PRICE_ID = os.getenv('STRIPE_PRICE_ID')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

# Validate that critical settings are set
if not STRIPE_SECRET_KEY:
    raise ValueError("STRIPE_SECRET_KEY is not set. Please set it in your environment variables.")

# Other API keys
DIFFBOT_API_KEY = os.getenv('DIFFBOT_API_KEY')

# Django secret key
SECRET_KEY = os.getenv('SECRET_KEY')

# AWS S3 settings
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'eu-west-2')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_VERIFY = True

# Media files configuration (S3)
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
MEDIA_ROOT = ''  # Leave empty when using S3
DEFAULT_FILE_STORAGE = 'agencies.storage_backends.MediaStorage'

# Additional S3 settings
AWS_DEFAULT_ACL = None
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

# Debug setting (use environment variable in production)
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Allowed hosts
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
if DEBUG:
    ALLOWED_HOSTS.extend([
        'travault-crm.herokuapp.com',
        '8000-tythetravel-travaultv2m-mpwcm7uefns.ws.codeinstitute-ide.net',
        'localhost',
        '127.0.0.1'
    ])

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'https://8000-tythetravel-travaultv2m-mpwcm7uefns.ws.codeinstitute-ide.net',
    'https://travault-crm.herokuapp.com'
]

# Application definition
INSTALLED_APPS = [
    'agencies',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_extensions',
    'billing.apps.BillingConfig',

    # Third-party apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'storages',
    'dal',
    'dal_select2',
    
    # Local apps
    'home',
    'agent_support',
    'crm',
    'activity_log',
    'dashboard',
    'tickets',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'billing.middleware.EnforcePaymentMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'travault_crm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',  # Enables template debugging
                'django.template.context_processors.request',  # Required by allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',  
]

# OTP settings
OTP_TOTP_ISSUER = "Travault-crm"

# Site configuration
SITE_ID = 1

# Email backend configuration
if 'DEVELOPMENT' in os.environ:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'Your Project <noreply@travault.com>'  
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASS')
    DEFAULT_FROM_EMAIL = os.getenv('EMAIL_HOST_USER')

WSGI_APPLICATION = 'travault_crm.wsgi.application'

# CSRF settings
CSRF_COOKIE_SECURE = True
CSRF_USE_SESSIONS = True

# Django AllAuth Configuration
# --------------------------- 

# User Model
AUTH_USER_MODEL = 'agencies.CustomUser'

# Authentication Settings
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_FORMS = {'signup': 'agencies.forms.AgencyRegistrationForm'}
ACCOUNT_ADAPTER = 'allauth.account.adapter.DefaultAccountAdapter'

# Email Settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = True
ACCOUNT_UNIQUE_EMAIL = True

# Password Settings
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True

# Username Settings
ACCOUNT_USERNAME_REQUIRED = True

# Session Settings
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True
ACCOUNT_LOGOUT_ON_GET = True

# URL Redirects
LOGIN_URL = '/'
LOGOUT_URL = 'agencies:account_logout'
LOGIN_REDIRECT_URL = 'dashboard:index'
LOGOUT_REDIRECT_URL = 'home'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_SIGNUP_REDIRECT_URL = 'agencies:registration_success'
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/agencies/login/'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = False

# Rate Limiting
ACCOUNT_RATE_LIMITS = {
    'login_failed': '5/300s',
}

# Template Overrides
ACCOUNT_LOGIN_TEMPLATE = 'account/account_login.html'
ACCOUNT_LOGOUT_TEMPLATE = 'account/account_logout.html'
ACCOUNT_PASSWORD_RESET_TEMPLATE = 'account/password_reset.html'
ACCOUNT_PASSWORD_RESET_DONE_TEMPLATE = 'account/password_reset_done.html'
ACCOUNT_PASSWORD_RESET_FROM_KEY_TEMPLATE = 'account/password_reset_from_key.html'
ACCOUNT_PASSWORD_RESET_FROM_KEY_DONE_TEMPLATE = 'account/password_reset_from_key_done.html'

# Redis/Celery settings
if 'UPSTASH_REDIS_URL' in os.environ:
    # Use Upstash Redis URL in production
    CELERY_BROKER_URL = os.environ.get('UPSTASH_REDIS_URL')
    CELERY_RESULT_BACKEND = os.environ.get('UPSTASH_REDIS_URL')
else:
    # Use local Redis in development
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Celery configuration
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://neondb_owner:m4ewnNkEHL5q@ep-dark-morning-a2kxwkeb.eu-central-1.aws.neon.tech/tutu_eats_boil_663773')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DATABASE_URL.split('/')[-1],
        'USER': DATABASE_URL.split('://')[1].split(':')[0],
        'PASSWORD': DATABASE_URL.split(':')[2].split('@')[0],
        'HOST': DATABASE_URL.split('@')[1].split('/')[0],
        'PORT': '5432',
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Ensure the 'logs' directory exists
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Logging configuration
LOGGING = {
    'version': 1,  # Specify the version of the logging configuration
    'disable_existing_loggers': False,  # Keep existing loggers active
    'formatters': {
        'verbose': {  # Detailed log format with timestamp and module
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {  # Simple log format with just the level and message
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {  # Handler for logging to a file
            'level': 'ERROR',  # Log only error messages
            'class': 'logging.FileHandler',  # Use FileHandler to write logs to a file
            'filename': os.path.join(BASE_DIR, 'logs/error.log'),  # Path to the log file
            'formatter': 'verbose',  # Use the verbose formatter for detailed logs
        },
        'console': {  # Handler for logging to the console
            'class': 'logging.StreamHandler',  # Use StreamHandler to output logs to the console
            'formatter': 'simple',  # Use the simple formatter for concise logs
        },
    },
    'loggers': {
        'django': {  # Logger for Django framework logs
            'handlers': ['file', 'console'],  # Use both file and console handlers
            'level': 'ERROR',  # Log only error messages
            'propagate': True,  # Allow log messages to propagate to parent loggers
        },
        'activity_log': {  # Logger for the 'activity_log' app
            'handlers': ['file', 'console'],  # Use both file and console handlers
            'level': 'ERROR',  # Log only error messages
            'propagate': False,  # Do not propagate to parent loggers
        },
    },
}