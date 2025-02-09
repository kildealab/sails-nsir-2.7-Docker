"""
Settings file which should be specified for running a development version of the site,
not a stable production (i.e. clinical) version
"""
from secret_dev_settings import *
from base_settings import *

DEBUG = True

TEMPLATE_DEBUG = DEBUG

WSGI_APPLICATION = 'ils.wsgi_dev.application'