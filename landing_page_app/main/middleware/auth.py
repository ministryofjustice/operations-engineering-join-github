import logging
from functools import wraps

from flask import (
    redirect,
    session,
)

logger = logging.getLogger(__name__)


def requires_auth(function_f):
    @wraps(function_f)
    def decorated(*args, **kwargs):
        logger.debug("requires_auth()")
        if "user" not in session:
            return redirect("/")
        return function_f(*args, **kwargs)

    return decorated
