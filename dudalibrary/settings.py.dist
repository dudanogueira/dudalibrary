# Django settings for dudalibrary project.

import os

from django.utils.translation import ugettext_lazy as _
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS

INSTANCE = lambda *x:os.path.join(os.path.dirname(__file__), *x)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'dev.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}


# SEARCH 

HAYSTACK_SEARCH_ENGINE = 'xapian'

HAYSTACK_SITECONF = 'dudalibrary.search_sites'

HAYSTACK_XAPIAN_PATH = INSTANCE('dudalibrary_search_index')

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.xapian_backend.XapianEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'xapian_index'),
    },
}

# CONTENTS PER PAGE TO SHOW AT RESULT (defaults to 10)
CONTENT_PER_PAGE = 10

# SOURCE PLUGINS AVAILABLE
# list item
SOURCE_PLUGINS =  ('portaldoprofessor', 'khanacademy', 'youtube')

# DONT TRANSLATE IT HERE, USE django i18n tools.
CONTENT_LANGUAGES = {
    'pt': _("Portuguese"),
    'en': _("English"),
    'es': _("Spanish"),
    'fr': _("French"),
    'gl': _("Galician"),
    'de': _("German"),
    'it': _("Italian"),
    'zh': _("Chinese"),
    'ca': _("Catalan"),
    'la': _("Latim"),
    'eo': _("Esperanto"),
    'na': _("Non Applicable"),
}

# log to command line use to log their activity
LOG_DIR = INSTANCE('logs')

# CONTENT_ROOT - Where files are stored. Default to
#CONTENT_ROOT = INSTANCE("../web-redable")
#CONTENT_ROOT = "/var/www/dudalibrary-content/archive/"
CONTENT_ROOT = "/Users/dudanogueira/Sites/web-redable/"

# CONTENT_URL - relative link where the files can be found thru the webserver
CONTENT_URL = "http://127.0.0.1/~dudanogueira/web-redable/"
#CONTENT_URL = "http://192.168.1.115/~dudanogueira/web-redable/"

#REPOSITORY_ROOT = "/Users/dudanogueira/WORK/workspace/contentserver-src/files/repository/"
#REPOSITORY_ROOT = INSTANCE("../web-redable/repository")
REPOSITORY_ROOT = "/Users/dudanogueira/Sites/web-redable/repository"
REPOSITORY_URL = "/archive/repository"

ADMIN_MEDIA_PREFIX = '/static/admin/'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Sao_Paulo'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pt-br'

LANGUAGES = (
    ('pt-br', 'Portugues'),
    ('es', 'Spanish'),
    ('en', 'English'),
)

LOCALE_PATHS = (
    INSTANCE('locale'),
)


SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = INSTANCE('media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = INSTANCE('static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'v#2xok#+oudtfu3e=@37b4(j+_la2ep#&amp;m5-+q3j6cv4of&amp;sim'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

ROOT_URLCONF = 'dudalibrary.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'dudalibrary.wsgi.application'

TEMPLATE_DIRS = (
    INSTANCE("templates/default/"),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # admin
    'django.contrib.admin',
    'django.contrib.admindocs',
    # third party apps
    'django_extensions',
    'south',
    'ratings',
    'tagging',
    'hitcount',
    # duda library apps
    'resources',
    'options',    
    'frontend',
    'curricular',
    'queue',
    'haystack',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}