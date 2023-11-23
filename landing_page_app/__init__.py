"""Flask App"""
import os
import logging

from flask import Flask
from flask_cors import CORS

from github import GithubException

from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from landing_page_app.main.scripts.github_script import GithubScript
from landing_page_app.main.views import (
    main,
    page_not_found,
    server_forbidden,
    unknown_server_error,
    handle_github_exception,
)


def create_app(github_script: GithubScript, rate_limit: bool = True) -> Flask:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s in %(module)s: %(message)s",
    )

    app = Flask(__name__, instance_relative_config=True)

    app.logger.info("Start App Setup")

    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["5 per minute", "1 per second"],
        storage_uri="memory://",
        strategy="moving-window",
    )

    limiter.init_app(app)
    limiter.enabled = rate_limit

    # Config folder file mapping
    config = {
        "development": "landing_page_app.config.development",
        "production": "landing_page_app.config.production",
    }

    # Set config, logging level and AWS DynamoDB table name
    if os.getenv("FLASK_CONFIGURATION", "production") == "development":
        app.config.from_object(config["development"])
        app.logger.setLevel(logging.DEBUG)
        app.logger.info("Running in Development mode.")
    else:
        app.config.from_object(config["production"])
        app.logger.setLevel(logging.INFO)
        app.logger.info("Running in Production mode.")

    # Load sensitive settings from instance/config.py
    app.config.from_pyfile("config.py", silent=True)

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

    app.logger.info("App Setup complete, running App...")
    return app
