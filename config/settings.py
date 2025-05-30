# config/settings.py

import os
from pathlib import Path
from decouple import config # Add this import

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# We'll use python-decouple for this. Create a .env file in your project root
# (teacherswapke_project/.env) and add: SECRET_KEY='your_strong_secret_key_here'
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool) # Example: DEBUG=False in .env for production

ALLOWED_HOSTS = [] # Configure as needed for deployment, e.g., ['yourdomain.com', 'www.yourdomain.com']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'crispy_forms',
    'crispy_bootstrap5',

    # My apps
    'users.apps.UsersConfig', # Custom user management app
    'swaps.apps.SwapsConfig', # Swap request and school details app
    'ai_assistant.apps.AiAssistantConfig', # AI chatbot and smart matching features app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', # Handles user sessions
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Handles user authentication
    'django.contrib.messages.middleware.MessageMiddleware', # For Django's messages framework
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Look for templates in the global 'templates' directory
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True, # Also look for templates in each app's 'templates' directory
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/stable/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3', # SQLite database file in the project root
    }
}


# Password validation
# https://docs.djangoproject.com/en/stable/ref/settings/#auth-password-validators
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
# https://docs.djangoproject.com/en/stable/topics/i18n/
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/stable/howto/static-files/
STATIC_URL = '/static/' # URL to serve static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'), # Directory where Django will look for static files
]
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_collected') # Uncomment and configure for production deployment

# Media files (User uploads)
MEDIA_URL = '/media/' # URL to serve user-uploaded files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') # Directory where user-uploaded files will be stored

# Crispy Forms Settings
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Custom User Model
AUTH_USER_MODEL = 'users.CustomUser' # Specifies our custom user model for authentication

# Default primary key field type
# https://docs.djangoproject.com/en/stable/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login and Logout Redirect URLs
LOGIN_URL = 'login' # Name of the URL pattern for the login page
LOGIN_REDIRECT_URL = 'swaps:dashboard'
LOGOUT_REDIRECT_URL = 'home' # URL name to redirect to after logout

# Email Configuration (Example for console backend during development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # Prints emails to console during development
# For actual email sending, configure SMTP settings (e.g., using SendGrid, Mailgun)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = config('EMAIL_HOST', default='localhost')
# EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)
# EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
# EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
# DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='webmaster@localhost')

# Django Messages Framework Storage (optional, but good for styling messages)
# from django.contrib.messages import constants as messages
# MESSAGE_TAGS = {
#     messages.DEBUG: 'alert-secondary',
#     messages.INFO: 'alert-info',
#     messages.SUCCESS: 'alert-success',
#     messages.WARNING: 'alert-warning',
#     messages.ERROR: 'alert-danger',
# }
# MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Gemini API Key (Add this to your .env file)
GOOGLE_API_KEY = config('GOOGLE_API_KEY', default='')
MPESA_CONSUMER_KEY = config('MPESA_CONSUMER_KEY', default='')
MPESA_CONSUMER_SECRET = config('MPESA_CONSUMER_SECRET', default='')
MPESA_SHORTCODE = config('MPESA_SHORTCODE', default='')
MPESA_PASSKEY = config('MPESA_PASSKEY', default='')
MPESA_CALLBACK_URL = config('MPESA_CALLBACK_URL', default='https://yourdomain.com/swaps/mpesa/callback/')

# PayPal Configuration
PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID', default='')
PAYPAL_CLIENT_SECRET = config('PAYPAL_CLIENT_SECRET', default='')
PAYPAL_MODE = config('PAYPAL_MODE', default='sandbox')
