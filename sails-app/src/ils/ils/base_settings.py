"""
Base Django settings for SaILS project, which are common to both a dev and production
version of the site. When running the site on a server, you should explicitly specify
either the dev or production settings, which inherit from this file.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from os.path import abspath, basename, dirname, join, normpath
from sys import path
from django.core.exceptions import ImproperlyConfigured

#-----------------------------------------------------------------------------------------
# Misc. Settings
#-----------------------------------------------------------------------------------------

VERSION = "1.0"
BUG_REPORT_URL = "https://bitbucket.org/lgmontgomery/sails_new/issues/new"
MAX_CACHE_TIMEOUT = 24*60*60*365
DEFAULT_TAXONOMY = "incidents_nsir"
NOTIFICATIONS_FAIL_SILENTLY = True
BASE_TEMPLATE = 'incidents_nsir/base_nsir.html'

# Toggle email backend (console vs smtp)
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

#LISTABLE_DOM =  '<"row"<"span6"ir><"span6"p>><"row"<"span12"rt>><"row"<"span12"lp>>'
LISTABLE_PAGINATION_TYPE = 'bootstrap2'

SITE_ID = 1

#Doesn't allow returning to same page (e.g. if running mulitple servers)
# Note this is overridden by the 'next' parameter specified on forms of the login pages
# To set new login page, change the 'next' parameter of navbar login and login template
LOGIN_REDIRECT_URL = "/nsir/dashboard"

# Do not automatically flag all submitted incidents
FLAG_ALL_ON_REPORT = False

# Allow/Disallow gating who can edit an investigation
GATE_EDITING = True

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'

#-----------------------------------------------------------------------------------------
# Path Configuration
#-----------------------------------------------------------------------------------------
# Absolute filesystem path to the Django project directory:
# e.g. /var/www/devDocuments/logan/projects/sails/ils
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Absolute filesystem path to the Django project directory:
# e.g. /var/www/devDocuments/logan/projects/sails/ils
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level project folder:
# e.g. /var/www/devDocuments/logan/projects/sails
SITE_ROOT = dirname(DJANGO_ROOT)

# Site name:
# e.g. ils
SITE_NAME = basename(DJANGO_ROOT)

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)

#-----------------------------------------------------------------------------------------
# Apps configuration
#--------------------------------------------------------------------------------------

DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'mod_wsgi.server',
)

THIRD_PARTY_APPS = (
    'south',
    'mptt',
    'django_mptt_admin',
    'listable',
    'adminsortable',
    'import_export',
    'djangojs',
    'fluent_comments',
    'crispy_forms',
    'django.contrib.comments',
)

LOCAL_APPS = (
    'accounts',
    'notifications_nsir',
)

# Specify taxonomy apps uniquely so can be easily reference from control app (model), which
# returns choice of taxonomies based on the following tuple
TAXONOMY_APPS = (
    'incidents_nsir',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS + TAXONOMY_APPS


#-----------------------------------------------------------------------------------------
# Fluent comments used on Investigation page.
#-----------------------------------------------------------------------------------------
COMMENTS_APP = 'fluent_comments'
FLUENT_COMMENTS_EXCLUDE_FIELDS = ('name', 'email', 'url')

#-----------------------------------------------------------------------------------------
# Middleware classes
#-----------------------------------------------------------------------------------------
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    #Custom middleware:
    'ils.middleware.middleware.RequestMiddleWare', #Display warning to IE Users
    'ils.middleware.middleware.updatelastvisit',
    'ils.middleware.middleware.AjaxRedirect',
)

ROOT_URLCONF = 'ils.urls'

#-----------------------------------------------------------------------------------------
# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
#-----------------------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Canada/Eastern'

DATETIME_FORMAT = 'F j, Y, g:i A'

USE_I18N = True

USE_L10N = False

USE_TZ = False


#-----------------------------------------------------------------------------------------
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
#-----------------------------------------------------------------------------------------
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
# STATIC_ROOT = normpath(join(BASE_DIR, 'assets'))
STATIC_ROOT = '/usr/src/data/static'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    normpath(join(BASE_DIR, 'static')),
)

#-----------------------------------------------------------------------------------------
# Media files 
#-----------------------------------------------------------------------------------------
MEDIA_URL = '/media/'

# MEDIA_ROOT = normpath(join(BASE_DIR, 'media'))
MEDIA_ROOT = '/usr/src/data/media'

# relative URL path for restricted media (only viewable if logged in)
RESTRICTED_MEDIA_URL = 'media/incidentimages/'

# Max allowed image file upload size (in MB)
MAX_IMAGE_SIZE = 5

#-----------------------------------------------------------------------------------------
# Fixtures
#-----------------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    normpath(join(SITE_ROOT, 'fixtures')),
)

#-----------------------------------------------------------------------------------------
# Templates
#-----------------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'absolute.context_processors.absolute',
    'ils.context_processors.info',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
# TEMPLATE_LOADERS = (
#     'django.template.loaders.filesystem.Loader',
#     'django.template.loaders.app_directories.Loader',
# )

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates'), os.path.join(BASE_DIR, 'templates/incidents_shared')]
# TEMPLATE_DIRS = (
#     normpath(join(SITE_ROOT, 'templates')),
#     normpath(join(SITE_ROOT, 'templates/incidents')),
# )

#-----------------------------------------------------------------------------------------
# Accounts/Users
#-----------------------------------------------------------------------------------------

AUTH_USER_MODEL = 'accounts.ILSUser'

#-----------------------------------------------------------------------------------------
# Celery
#-----------------------------------------------------------------------------------------
CELERY_REDIS_HOST = 'redis'
BROKER_URL = 'redis://redis_sails27:6379'
CELERY_RESULT_BACKEND = 'redis://redis_sails27:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'


def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return os.environ[setting]
    except KeyError:
        error_msg = "Set the %s env variable" % setting
        raise ImproperlyConfigured(error_msg)
