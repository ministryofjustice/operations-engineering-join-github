import sys
import logging
from os import environ
from dotenv import dotenv_values

from join_github_app.main.services.github_service import GithubService
from join_github_app import create_app


def get_tokens():
    github_token = environ.get("ADMIN_GITHUB_TOKEN")
    if not github_token:
        # Look for a local .env file
        github_token = dotenv_values(".env").get("ADMIN_GITHUB_TOKEN")
        if not github_token:
            logging.error("Failed to find a GitHub Token")
            sys.exit(1)
    return github_token


def build_app():
    github_token = get_tokens()
    github_service = GithubService(github_token)
    return create_app(github_service)


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
