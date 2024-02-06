import logging

import sentry_sdk
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader
from sentry_sdk.integrations.flask import FlaskIntegration

from app.app_config import app_config
from app.main.middleware.error_handler import (
    page_not_found,
    server_forbidden,
    unknown_server_error,
)
from app.main.routes.auth import auth_route
from app.main.routes.join import join_route
from app.main.routes.main import main
from app.main.services.github_service import GithubService


def create_app(
    github_service=GithubService(app_config.github.token), rate_limit: bool = True
) -> Flask:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s in %(module)s: %(message)s",
    )

    if app_config.sentry.dsn_key and app_config.sentry.environment:
        sentry_sdk.init(
            dsn=app_config.sentry.dsn_key,
            environment=app_config.sentry.environment,
            integrations=[FlaskIntegration()],
            enable_tracing=True,
            traces_sample_rate=0.1,
        )

    app = Flask(__name__, instance_relative_config=True)

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

    app.secret_key = app_config.flask.app_secret_key

    app.register_blueprint(auth_route, url_prefix="/auth")
    app.register_blueprint(join_route, url_prefix="/join")
    app.register_blueprint(main)

    app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("app"),
            PrefixLoader(
                {"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}
            ),
        ]
    )
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.globals["phase_banner_text"] = app_config.phase_banner_text

    app.register_error_handler(403, server_forbidden)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, unknown_server_error)

    CORS(app, resources={r"/*": {"origins": "*", "send_wildcard": "False"}})

    app.github_service = github_service

    app.logger.info("App Setup complete, running App...")
    return app
