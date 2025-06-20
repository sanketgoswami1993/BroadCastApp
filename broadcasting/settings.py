"""
Django settings for broadcasting project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'b+d82tsg4ggs#(*1a71**3slk&1_*j(9h)3_@a^phrp62+rm00'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #Third Party Apps
    'push_notifications',
    'rest_framework',
    'rest_framework.authtoken',

    #local apps
    'info',
    'node_hierarchy',
    'message',
    'configure',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'broadcasting.urls'

WSGI_APPLICATION = 'broadcasting.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST' : 'localhost',
        'USER' : 'root',
        'PASSWORD' : 'root',
        'NAME': 'broadcasting',
        'PORT' : 3306,
        #'OPTIONS': {'charset': 'utf8mb4'},
    }
}


## Rest framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# SMS Settings
SMS_TEXT_LOCAL_API_KEY = 't57iVIdpe5I-KPsN5fOZp3umnN0Yfipqs2P2EvT1Qe'
SMS_TEXT_LOCAL_HASH_KEY = '3c7616a045bda6767855e72722a4c5c8efdefdfd'
SENDER_NAME = 'TXTLCL'
SMS_TEXT_LOCAL_EMAIL = 'nareshtest@quixom.com'

#Email settings
FROM_EMAIL  = 'egramsetu@gmail.com'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'egramsetu@gmail.com'
EMAIL_HOST_PASSWORD = 'egramsetu_123'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

## PUSH NOTIFICATION
PUSH_NOTIFICATIONS_SETTINGS = {
        "GCM_API_KEY": "AIzaSyDU9MRCCvj351qol8M7n2GX96yKlSX5g28",
}
PUSH_NOTIFICATIONS_MESSAGE_ID = {
    'login': {'id': '1'},
    'msg-to-all': {'id' : '2'},
    'approve-msg-controller' : {'id': '3'},
    'staff-msg-approve': {'id': '4'},
    'staff-register-controller': {'id': '5'}
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'


#Media
UPLOAD_TO = 'attachments'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'

#message string
REGISTRATION_SMS_TEXT = """ You are registered in EgramSetu App as %s from %s.
You can set password using OTP. Your OTP is %s.
If you don't have EgramSetu Application, you can download from
here. https://play.google.com/store/apps/details?id=com.quixom.broadcastapp
"""

FORGOT_OTP_MSG = """ E-%s is your EgramSetu verification code. """
