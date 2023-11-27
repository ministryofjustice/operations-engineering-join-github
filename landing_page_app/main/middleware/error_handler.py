import logging

from flask import (
    render_template,
)

logger = logging.getLogger(__name__)


def handle_github_exception(error_message):
    logger.error("GitHub exception occurred: %s", error_message)
    return render_template("internal-error.html", error_message=error_message)


def page_not_found(err):
    logger.error("A request was made to a page that doesn't exist %s", err)
    return render_template("404.html"), 404


def server_forbidden(err):
    logger.error("server_forbidden(): %s", err)
    return render_template("403.html"), 403


def unknown_server_error(err):
    logger.error("An unknown server error occurred: %s", err)
    return render_template("500.html"), 500


def gateway_timeout(err):
    logger.error("A gateway timeout error occurred: %s", err)
    return render_template("504.html"), 504
