"""
Settings for testing the application.
"""
DEBUG = True

DJANGO_RDFLIB_DEVELOP = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'rdflib_django.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        }
}

SITE_ID = 1

STATIC_URL = '/static/'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',

    'rdflib_django',
    )
ROOT_URLCONF = 'rdflib_django.urls'