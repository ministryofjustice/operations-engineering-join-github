""" Config values to be used during development """
import os

from os import environ

APP_SECRET_KEY = environ.get("APP_SECRET_KEY")
FLASK_CONFIGURATION = "development"
DEBUG = True
FLASK_DEBUG = True
MAIL_FROM_EMAIL = "operations-engineering@digital.justice.gov.uk"
PORT = 4567
SSL_REDIRECT = False
TESTING = True

if not APP_SECRET_KEY:
    os.environ["APP_SECRET_KEY"] = "dev"
