import logging

from flask import render_template

logger = logging.getLogger(__name__)


def client_error(err: Exception):
    logger.error("There was an error with the client request %s", err)
    return render_template("pages/errors/400.html", error_message=str(err)), 400


def page_not_found(err: Exception):
    logger.error("A request was made to a page that doesn't exist %s", err)
    return render_template("pages/errors/404.html"), 404


def server_forbidden(err: Exception):
    logger.error("server_forbidden(): %s", err)
    return render_template("pages/errors/403.html"), 403


def unknown_server_error(err: Exception):
    logger.error("An unknown server error occurred: %s", err)
    return render_template("pages/errors/500.html"), 500


def gateway_timeout(err: Exception):
    logger.error("A gateway timeout error occurred: %s", err)
    return render_template("pages/errors/504.html"), 504


class AuthTokenError(Exception):
    """Custom exception for Auth token retrieval errors."""

    def __init__(self, message, original_exception=None):
        """
        Initialize the AuthTokenError.

        :param message: A message describing the error.
        :param original_exception: The original exception that caused this error, if any.
        """
        super().__init__(message)
        self.message = message
        self.original_exception = original_exception

    def __str__(self):
        """
        String representation of the error.
        """
        if self.original_exception:
            return f"{self.message} (Caused by {self.original_exception})"
        return self.message
