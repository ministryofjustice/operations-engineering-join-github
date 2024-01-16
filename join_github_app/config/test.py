""" Config values to be used during development """
from os import environ

DEBUG = True
FLASK_DEBUG = True
MAIL_FROM_EMAIL = "operations-engineering@digital.justice.gov.uk"
PORT = 4567
SSL_REDIRECT = False
TESTING = True
AUTH0_CLIENT_ID = environ.get("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = environ.get("AUTH0_CLIENT_SECRET")
AUTH0_DOMAIN = environ.get("AUTH0_DOMAIN")
APP_SECRET_KEY = environ.get("APP_SECRET_KEY")
SELECTABLE_ORGANISATIONS = [
    {'value': 'ministryofjustice', 'text': 'Ministry of Justice'},
    {'value': 'analytical-services', 'text': 'MoJ Analytical Services'}
]
