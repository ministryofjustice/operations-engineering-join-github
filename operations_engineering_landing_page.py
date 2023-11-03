"""operations-engineering-landing-page"""
import sys
import logging
from os import environ
from dotenv import dotenv_values

from landing_page_app.main.services.slack_service import SlackService
from landing_page_app.main.services.github_service import GithubService
from landing_page_app.main.scripts.github_script import GithubScript
from landing_page_app import create_app


def get_tokens():
    github_token = environ.get("GH_TOKEN")
    if not github_token:
        # Look for a local .env file
        github_token = dotenv_values(".env").get("GH_TOKEN")
        if not github_token:
            logging.error("Failed to find a GitHub Token")
            sys.exit(1)

    slack_token = environ.get("SLACK_TOKEN")
    if not slack_token:
        # Look for a local .env file
        slack_token = dotenv_values(".env").get("SLACK_TOKEN")
        if not slack_token:
            logging.error("Failed to find a Slack Token")
            sys.exit(1)

    recaptcha_public_key = environ.get("RECAPTCHA_PUBLIC_KEY")
    if not recaptcha_public_key:
        # Look for a local .env file
        recaptcha_public_key = dotenv_values(".env").get("RECAPTCHA_PUBLIC_KEY")
        if not recaptcha_public_key:
            logging.error("Failed to find recaptcha public key")
            sys.exit(1)

    recaptcha_private_key = environ.get("RECAPTCHA_PRIVATE_KEY")
    if not recaptcha_private_key:
        # Look for a local .env file
        recaptcha_private_key = dotenv_values(".env").get("RECAPTCHA_PRIVATE_KEY")
        if not recaptcha_private_key:
            logging.error("Failed to find recaptcha private key")
            sys.exit(1)

    return github_token, slack_token, recaptcha_public_key, recaptcha_private_key


def build_app():
    github_token, slack_token, recaptcha_public_key, recaptcha_private_key = get_tokens()
    github_service = GithubService(github_token)
    github_script = GithubScript(github_service)
    slack_service = SlackService(slack_token)
    return create_app(github_script, slack_service, recaptcha_public_key, recaptcha_private_key)


# Gunicorn entry point, return the object without running it
def app():
    return build_app()


# Run Flask locally entry point for makefile and debugger
def run_app():
    flask_app = build_app()
    flask_app.run(port=4567)
    return flask_app


if __name__ == "__main__":
    run_app()
