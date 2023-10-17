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
    return github_token, slack_token


def build_app():
    github_token, slack_token = get_tokens()
    github_service = GithubService(github_token)
    github_script = GithubScript(github_service)
    slack_service = SlackService(slack_token)
    return create_app(github_script, slack_service)


# Gunicorn entry point, return the object without running it
def app():
    return build_app()


# Run Flask locally entry point for makefile and debugger
def run_app():
    app = build_app()
    app.run(port=4567)
    return app


if __name__ == "__main__":
    run_app()
