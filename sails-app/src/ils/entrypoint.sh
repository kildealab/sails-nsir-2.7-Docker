#!/bin/bash
cp -r assets/* /app/data/static
cp -r incidents_nsir/php_templates/* /app/data/php_emr
/usr/bin/python manage.py syncdb --settings=ils.prod_settings

/usr/bin/python manage.py migrate accounts --settings=ils.prod_settings
/usr/bin/python manage.py migrate incidents_nsir --settings=ils.prod_settings
/usr/bin/python manage.py migrate notifications_nsir --settings=ils.prod_settings

/usr/bin/python manage.py loaddata accounts/fixtures/*.json --settings=ils.prod_settings
/usr/bin/python manage.py loaddata incidents_nsir/fixtures/*.json --settings=ils.prod_settings
/usr/bin/python manage.py loaddata notifications_nsir/fixtures/*.json --settings=ils.prod_settings

/usr/bin/python manage.py shell < installation/create_superuser.py --settings=ils.prod_settings
/usr/bin/python installation/replace_dependencies.py

/usr/local/bin/gunicorn ils.wsgi:application --bind "0.0.0.0:8000"
