"""Flask App"""
import logging

from flask import Flask
from flask_cors import CORS

from github import GithubException

from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader

from landing_page_app.main.scripts.github_script import GithubScript
from landing_page_app.main.services.slack_service import SlackService
from landing_page_app.main.views import (
    main,
    page_not_found,
    server_forbidden,
    unknown_server_error,
    handle_github_exception,
)


def create_app(github_script: GithubScript, slack_service: SlackService) -> Flask:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s in %(module)s: %(message)s",
    )

    app = Flask(__name__, instance_relative_config=True)

    app.logger.info("Start App Setup")

    # Set the config file and logging level
    app.logger.setLevel(logging.DEBUG)
    app.config.from_object("landing_page_app.config.development")
    app.logger.info("Running in Development mode.")

    app.secret_key = app.config.get("APP_SECRET_KEY")

    app.register_blueprint(main)

    app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("landing_page_app"),
            PrefixLoader(
                {"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}
            ),
        ]
    )

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    app.register_error_handler(403, server_forbidden)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, unknown_server_error)
    app.register_error_handler(GithubException, handle_github_exception)

    # Security and Protection extenstions
    CORS(app, resources={r"/*": {"origins": "*", "send_wildcard": "False"}})

    app.github_script = github_script
    app.slack_service = slack_service

    app.logger.info("App Setup complete, running App...")

    return app
