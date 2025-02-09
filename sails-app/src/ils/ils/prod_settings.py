"""
Settings file which should be specified for running a stable production (i.e. clinical)
version of the site, not the development version.
"""
from secret_prod_settings import *
from base_settings import *

DEBUG = False

TEMPLATE_DEBUG = DEBUG

WSGI_APPLICATION = 'ils.wsgi_prod.application'
