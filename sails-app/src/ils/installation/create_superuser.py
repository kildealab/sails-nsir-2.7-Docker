import os

# from django.contrib.auth.models import User
from accounts.models import ILSUser
from django.db import IntegrityError

# getting name,email & password from env variables
DJANGO_SUPERUSER_USERNAME = os.environ.get('DJANGO_SUPERUSER_USERNAME')
DJANGO_SUPERUSER_PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
DJANGO_SUPERUSER_EMAIL = os.environ.get('DJANGO_SUPERUSER_EMAIL')
DJANGO_SUPERUSER_FIRST_NAME = os.environ.get('DJANGO_SUPERUSER_FIRST_NAME')
DJANGO_SUPERUSER_LAST_NAME = os.environ.get('DJANGO_SUPERUSER_LAST_NAME')

try:
    superuser = ILSUser.objects.create_superuser(
        username=DJANGO_SUPERUSER_USERNAME,
        email=DJANGO_SUPERUSER_EMAIL,
        password=DJANGO_SUPERUSER_PASSWORD,
        first_name=DJANGO_SUPERUSER_FIRST_NAME,
        last_name=DJANGO_SUPERUSER_LAST_NAME,
        must_change_password=False
        )
    superuser.save()
except IntegrityError:
    print("Super User with username %s already present" % DJANGO_SUPERUSER_USERNAME)
except Exception as e:
    print(e)

