"""
Sensitive settings which should not be shared when serving the website, nor on remote
repositories.

Copy the following settings-level variables into a local file (within this directory)
named secret_settings.py. Or if using distinct dev and production settings files,
include files: secret_dev_settings.py and secret_prod_settings.py Enter the sensitive
data/passwords accordingly and note that the corresponding file will not be included in
the  git commit history.
"""
#-----------------------------------------------------------------------------------------
# Email settings
#-----------------------------------------------------------------------------------------
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'myname@gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_PASSWORD = 'mypassword'

CONTACT_EMAIL = "myname@gmail.com"
NOTIFICATIONS_EMAIL = "myname@gmail.com"
DEFAULT_FROM_EMAIL = "myname@gmail.com"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'mysecretkeyq3940fjajfsadkf93'

ANONYMOUS_DISPLAY = False # Set to True if want to hide names (demo purposes)

#-----------------------------------------------------------------------------------------
# Usernames of SaILS users who should be notified for all anonymous incident reports
#-----------------------------------------------------------------------------------------
ILS_MANAGERS = []

#-----------------------------------------------------------------------------------------
# Investigator (usernames) that are suggested at the time of incident report based on the
# role (accounts.Role) of the user who is submitting the report
#-----------------------------------------------------------------------------------------
#INVESTIGATOR_DEMO = 'myusername'
INVESTIGATOR_ANONYMOUS = '' # anonymous users (not logged in)
INVESTIGATOR_ADMIN = '' # admin users (likely for testing in dev version)
INVESTIGATOR_THERAPY = '' # for RTT Reports
INVESTIGATOR_DOSIMETRY = '' # for dosimetry reports
INVESTIGATOR_PHYSICS = '' # for physics reports
INVESTIGATOR_ONCOLOGY = '' # for oncology reports

#-----------------------------------------------------------------------------------------
# The URL at which PHP scripts (connection with EMR functionality) may be accessed
#-----------------------------------------------------------------------------------------
PHP_DIR = '' # e.g. http://127.0.0.1/domain/php_scripts/

#-----------------------------------------------------------------------------------------
# Production only settings
#-----------------------------------------------------------------------------------------
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

#-----------------------------------------------------------------------------------------
# Links to user tutorials, etc.
#-----------------------------------------------------------------------------------------
TUTORIALS = {
    'report': {
        'show': False,
        'text': '',
        'url': '', #e.g: http://127.0.0.1/depdocs/node/####
    },
    'investigation': {
        'show': False,
        'text': '',
        'url': '',
    },
    'disclosure': {
        'show': False,
        'text': '',
        'url': '',
    },
    'nsir': {
        'show': False,
        'text': '',
        'url': 'https://www.ncbi.nlm.nih.gov/pubmed/27068779',
    },
}
