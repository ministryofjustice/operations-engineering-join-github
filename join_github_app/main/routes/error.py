import logging

from flask import Blueprint, render_template

error_route = Blueprint('error_route', __name__)

logger = logging.getLogger(__name__)


def error(error_message):
    logger.error(error_message)
    return render_template(
        "pages/errors/internal-error.html", error_message=error_message
    )
