from os import environ

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

SEND_EMAIL_INVITES = environ.get("SEND_EMAIL_INVITES")
