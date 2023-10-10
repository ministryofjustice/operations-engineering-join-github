""" Config file to load .env file variables for local development
"""
from os import environ
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

APP_SECRET_KEY = environ.get("APP_SECRET_KEY")

