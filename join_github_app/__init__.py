"""Flask App"""
import logging
import os
import sentry_sdk

from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from github import GithubException
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader
from join_github_app.main.middleware.error_handler import (
    handle_github_exception,
    page_not_found,
    server_forbidden,
    unknown_server_error,
)
from join_github_app.main.routes.auth import auth_route
from join_github_app.main.routes.join import join_route
from join_github_app.main.routes.error import error_route
from join_github_app.main.services.github_service import GithubService
from join_github_app.main.routes.main import main
from sentry_sdk.integrations.flask import FlaskIntegration


def create_app(github_service: GithubService, rate_limit: bool = True) -> Flask:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s in %(module)s: %(message)s",
    )

    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN_KEY"),
        integrations=[FlaskIntegration()],
        enable_tracing=True,
        traces_sample_rate=0.1
    )

    app = Flask(__name__, instance_relative_config=True)

    @app.context_processor
    def inject_os():
        return dict(os=os)

    app.logger.info("Start App Setup")

    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["10 per minute", "2 per second"],
        storage_uri="memory://",
        strategy="moving-window",
    )

    limiter.init_app(app)
    limiter.enabled = rate_limit

    # Config folder file mapping
    config = {
        "development": "join_github_app.config.development",
        "production": "join_github_app.config.production",
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

    app.register_blueprint(auth_route, url_prefix='/auth')
    app.register_blueprint(join_route, url_prefix='/join')
    app.register_blueprint(error_route, url_prefix='/error')
    app.register_blueprint(main)

    app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("join_github_app"),
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

    app.github_service = github_service

    app.logger.info("App Setup complete, running App...")
    return app
