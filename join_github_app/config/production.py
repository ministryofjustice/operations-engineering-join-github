""" Config values to be used in production """
from os import environ

DEBUG = False
FLASK_DEBUG = False
MAIL_FROM_EMAIL = "operations-engineering@digital.justice.gov.uk"
PORT = 4567
SSL_REDIRECT = True
TESTING = False
AUTH0_CLIENT_ID = environ.get("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = environ.get("AUTH0_CLIENT_SECRET")
AUTH0_DOMAIN = environ.get("AUTH0_DOMAIN")
APP_SECRET_KEY = environ.get("APP_SECRET_KEY")
SELECTABLE_ORGANISATIONS = [
    {'value': 'ministryofjustice', 'text': 'Ministry of Justice'},
    {'value': 'moj-analytical-services', 'text': 'MoJ Analytical Services'}
]
