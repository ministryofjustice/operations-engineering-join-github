"""Flask App"""
from dotenv import dotenv_values

import logging

from flask import Flask
from flask_cors import CORS

from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader

from landing_page_app.main.services.github_service import GithubService
from landing_page_app.main.views import (main, page_not_found, server_forbidden, unknown_server_error)


def create_app() -> Flask:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s in %(module)s: %(message)s',
    )

    app = Flask(__name__, instance_relative_config=True)

    # app.logger.setLevel(logging.DEBUG)
    # app.logger.formatter('%(asctime)s %(levelname)s in %(module)s: %(message)s')
    app.logger.info("Start App Setup")

    # Set config file and logging level
    app.config.from_object("landing_page_app.config.development")

    app.logger.info("Running in Development mode.")

    app.secret_key = app.config.get("APP_SECRET_KEY")

    app.register_blueprint(main)

    app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("landing_page_app"),
            PrefixLoader({"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}),
        ]
    )

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    app.register_error_handler(403, server_forbidden)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, unknown_server_error)

    # Security and Protection extenstions
    CORS(app, resources={r"/*": {"origins": "*", "send_wildcard": "False"}})

    app.config.update(GITHUB_TOKEN=dotenv_values(".env").get("GITHUB_TOKEN"))
    github_token = app.config.get("GITHUB_TOKEN")
    if not github_token:
        logging.error("Get the GitHub Token error")
        exit(1)
    app.github_service = GithubService(github_token)

    app.logger.info("App Setup complete, running App...")

    return app
