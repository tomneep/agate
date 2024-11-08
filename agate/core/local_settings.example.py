"""
Settings that are specific to this particular instance of the project.
This can contain sensitive information (such as keys) and should not be shared with others.

REMEMBER: If modfiying the content of this file, reflect the changes in local_settings.example.py
"""

import os
from varys_message_retrieval import VarysMessageRetrieval

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create a SECRET_KEY.
# from django.core.management.utils import get_random_secret_key
# get_random_secret_key()
SECRET_KEY = ''

# Set to True if in development, or False is in production
DEBUG = True/False

# Set to ['*'] if in development, or specific IP addresses and domains if in production
ALLOWED_HOSTS = ['*']/['django-template.bham.ac.uk']

# Provide the email address for the site admin (e.g. the researcher/research team)
ADMIN_EMAIL = '...@bham.ac.uk'

# Set the database name below
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'django-template.sqlite3'),
        'TEST': {
            'NAME': os.path.join(BASE_DIR, 'django-template_TEST.sqlite3'),
        },
    }
}

ONYX_DOMAIN = ''

MESSAGE_RETRIEVAL = VarysMessageRetrieval(
                              config_path="varys_config.cfg",
                              profile="test",
                              logfile="varys.log",
                              log_level="DEBUG",
                              auto_acknowledge=False)
