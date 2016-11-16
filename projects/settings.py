"""
Django settings for projects project.

Generated by 'django-admin startproject' using Django 1.9.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import environ
root = environ.Path(__file__) - 2
default_db_name = str(root.path('project_status_dashboard.db'))
env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, "DONT USE IN PRODUCTION LIKE THIS"),
    DB_NAME=(str, default_db_name),
    REDIS_URL=(str, ""),
    REDIS_DB=(int, 1),
    GOOGLE_SPREADSHEET_ID=(str),
    JIRA_URL=(str),
    JIRA_AUTH=(tuple, ()),
    JIRA_DONE=(list, ["Abandoned", "Done", "Deployed", "In Test Review", "Test Review Complete", "Closed"]),
    JIRA_SSL_VERIFY=(bool, True),
    ALLOWED_HOSTS=(list, ["*", ]),
)  # set default values and casting
environ.Env.read_env(str(root.path('.env')))  # reading .env file

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env('ALLOWED_HOSTS')


# Application definition

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'dashboard',
    'django_rq',
]

MIDDLEWARE_CLASSES = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'projects.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'dashboard.context_processors.jira_url',
            ],
        },
    },
]

WSGI_APPLICATION = 'projects.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': env('DB_NAME'),
    }
}

if env('REDIS_URL'):
    CACHES = {
        'default': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': env('REDIS_URL'),
            'OPTIONS': {
                'DB': env('REDIS_DB'),
            }
        },
    }

    RQ_QUEUES = {
        'default': {
            'USE_REDIS_CACHE': 'default',
        },
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        },
    }
    # Tell queus not to be async, give it a bogus redis config
    RQ_QUEUES = {
        'default': {
            'HOST': 'localhost',
            'PORT': 6379,
            'DB': 0,
            'ASYNC': False
        },
    }

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = "America/New_York"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = str(root.path('static'))
STATICFILES_DIRS = ()

GOOGLE_SPREADSHEET_ID = env('GOOGLE_SPREADSHEET_ID')
JIRA_URL = env('JIRA_URL')
JIRA_AUTH = env('JIRA_AUTH')
JIRA_DONE = env('JIRA_DONE')
JIRA_SSL_VERIFY = env('JIRA_SSL_VERIFY')

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s %(message)s",
            "datefmt": "%H:%M:%S",
        },
    },
    "handlers": {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        "rq_console": {
            "level": "INFO",
            "class": "rq.utils.ColorizingStreamHandler",
            "formatter": "simple",
            "exclude": ["%(asctime)s"],
        },
    },
    'loggers': {
        "dashboard": {
            "handlers": ["console", ],
            "formatter": "simple",
            "level": "INFO",
        },
        "rq.worker": {
            "handlers": ["console", ],
            "formatter": "simple",
            "level": "INFO",
        },
        "rq.scheduler": {
            "handlers": ["console", ],
            "formatter": "simple",
            "level": "INFO",
        },
        "dashboard.services.jira": {
            "handlers": ["console", ],
            "formatter": "simple",
            "level": "WARNING"
        },
        "dashboard.services.jira.summarize_results": {
            "handlers": ["console", ],
            "formatter": "simple",
            "level": "INFO"
        },
        'requests': {
            # The requests library is too verbose in it's logging, reducing the verbosity in our logs.
            'handlers': ["console", ],
            'level': 'WARNING',
            'propagate': True,
        },
        'urllib3': {
            'handers': ["console", ],
            'level': 'WARNING',
            'propagate': True
        },
    }
}
