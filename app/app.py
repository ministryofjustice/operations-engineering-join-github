import logging

from flask import Flask

from app.main.config.app_config import app_config
from app.main.config.cors_config import configure_cors
from app.main.config.error_handlers_config import configure_error_handlers
from app.main.config.jinja_config import configure_jinja
from app.main.config.limiter_config import configure_limiter
from app.main.config.logging_config import configure_logging
from app.main.config.routes_config import configure_routes
from app.main.config.sentry_config import configure_sentry
from app.main.services.auth0_service import Auth0_Service
from app.main.services.github_service import GithubService

logger = logging.getLogger(__name__)


def create_app(
    github_service=GithubService(app_config.github.token), is_rate_limit_enabled=True
) -> Flask:
    configure_logging(app_config.logging_level)

    logger.info("Starting app...")

    app = Flask(__name__)

    app.secret_key = app_config.flask.app_secret_key

    app.github_service = github_service
    app.auth0_service = Auth0_Service(
        app,
        app_config.auth0.client_id,
        app_config.auth0.client_secret,
        app_config.auth0.domain,
    )

    configure_routes(app)
    configure_error_handlers(app)
    configure_sentry(app_config.sentry.dsn_key, app_config.sentry.environment)
    configure_limiter(app, is_rate_limit_enabled)
    configure_jinja(app)
    configure_cors(app)

    logger.info("Running app...")

    return app
