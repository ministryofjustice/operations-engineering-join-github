"""operations-engineering-landing-page"""
import logging
from os import environ
from dotenv import dotenv_values

from landing_page_app.main.services.github_service import GithubService
from landing_page_app.main.scripts.github_script import GithubScript
from landing_page_app import create_app


def run_app():
    github_token = environ.get('GITHUB_TOKEN')
    if not github_token:
        github_token = dotenv_values(".env").get("GITHUB_TOKEN")
        if not github_token:
            logging.error("Failed to find a GitHub Token")
            exit(1)
    github_service = GithubService(github_token)
    github_script = GithubScript(github_service)
    app = create_app(github_script)
    app.run(port=app.config.get("PORT", 4567))


if __name__ == "__main__":
    run_app()
