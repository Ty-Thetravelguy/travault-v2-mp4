from pathlib import Path
import os
from dotenv import load_dotenv
from storages.backends.s3boto3 import S3Boto3Storage


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file in project root
ENV_FILE = BASE_DIR / '.env'

load_dotenv(ENV_FILE)

STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PRICE_ID = os.getenv('STRIPE_PRICE_ID')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

# Validate that critical settings are set
if not STRIPE_SECRET_KEY:
    raise ValueError("STRIPE_SECRET_KEY is not set. Please set it in your environment variables.")

# Access variables
DIFFBOT_API_KEY = os.getenv('DIFFBOT_API_KEY')

SECRET_KEY = os.getenv('SECRET_KEY')

BASE_DIR = Path(__file__).resolve().parent.parent

# AWS S3 settings
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'eu-west-2')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_VERIFY = True

# Media files configuration (S3)
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
MEDIA_ROOT = ''  # Leave empty when using S3

DEFAULT_FILE_STORAGE = 'agencies.storage_backends.MediaStorage'

# Additional S3 settings
AWS_DEFAULT_ACL = None
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

# Debug setting (use environment variable in production)
DEBUG = os.getenv('DEBUG', 'False') == 'False'

DEBUG = True


# Allowed hosts
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
if DEBUG:
    ALLOWED_HOSTS.extend([
        'travault-crm.herokuapp.com',
        '8000-tythetravel-travaultv2m-mpwcm7uefns.ws.codeinstitute-ide.net',
        'localhost',
        '127.0.0.1'
    ])
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
                'django.template.context_processors.debug',
                'django.template.context_processors.request', #required by allauth
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

OTP_TOTP_ISSUER = "Travault-crm"

SITE_ID = 1

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Your Project <noreply@travault.com>'  

WSGI_APPLICATION = 'travault_crm.wsgi.application'

CSRF_COOKIE_SECURE = True
CSRF_USE_SESSIONS = True

# Allauth settings
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = False
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/agencies/login/'
LOGIN_URL = '/'  # Should point to your custom login view
LOGOUT_URL = 'agencies:account_logout'
LOGIN_REDIRECT_URL = 'dashboard:index'
LOGOUT_REDIRECT_URL = 'home'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_RATE_LIMITS = {
    'login_failed': '5/300s',
}
ACCOUNT_FORMS = {'signup': 'agencies.forms.AgencyRegistrationForm'}
ACCOUNT_ADAPTER = 'allauth.account.adapter.DefaultAccountAdapter'
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_UNIQUE_EMAIL = True


# Add these lines to specify your custom templates
ACCOUNT_LOGIN_TEMPLATE = 'account/account_login.html'
ACCOUNT_LOGOUT_TEMPLATE = 'account/account_logout.html'
ACCOUNT_PASSWORD_RESET_TEMPLATE = 'account/password_reset.html'
ACCOUNT_PASSWORD_RESET_DONE_TEMPLATE = 'account/password_reset_done.html'
ACCOUNT_PASSWORD_RESET_FROM_KEY_TEMPLATE = 'account/password_reset_from_key.html'
ACCOUNT_PASSWORD_RESET_FROM_KEY_DONE_TEMPLATE = 'account/password_reset_from_key_done.html'

AUTH_USER_MODEL = 'agencies.CustomUser'

# Redis as the broker and result backend
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Optional Celery settings
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC' 

CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://neondb_owner:R4QrxfC0MBla@ep-purple-grass-a2m3x556.eu-central-1.aws.neon.tech/barn_otter_coast_427430')

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
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True




# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Ensure the 'logs' directory exists
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/error.log'),
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'activity_log': {  # Your app's name
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}