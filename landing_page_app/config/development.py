""" Config values to be used during development """
from os import environ

FLASK_CONFIGURATION = "development"
DEBUG = True
FLASK_DEBUG = True
MAIL_FROM_EMAIL = "operations-engineering@digital.justice.gov.uk"
PORT = 4567
SSL_REDIRECT = False
TESTING = True

if environ.get("APP_SECRET_KEY") is None:
    environ["APP_SECRET_KEY"] = "dev"
    APP_SECRET_KEY = environ.get("APP_SECRET_KEY")
else:
    APP_SECRET_KEY = environ.get("APP_SECRET_KEY")
