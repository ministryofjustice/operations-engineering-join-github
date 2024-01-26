import logging
import os
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from flask import (Blueprint, current_app, redirect, render_template, session,
                   url_for)

from join_github_app.main.config.constants import ALLOWED_EMAIL_DOMAINS

logger = logging.getLogger(__name__)

auth_route = Blueprint("auth_routes", __name__)

oauth = OAuth(current_app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)


@auth_route.route("/login")
def login():
    """
    Redirects the user to auth0
    """
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("auth_routes.callback", _external=True, _scheme="https")
    )


@auth_route.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(
        "https://"
        + os.getenv("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("main.index", _external=True),
                "client_id": os.getenv("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


@auth_route.route("/callback", methods=["GET", "POST"])
def callback():
    try:
        token = oauth.auth0.authorize_access_token()
        session["user"] = token
    except (KeyError, AttributeError):
        return render_template("pages/errors/500.html"), 500

    auth0_email = session["user"]["userinfo"]["email"]
    # original_email is how the user initialises the flask app journey
    original_email = session["email"]

    if user_is_valid(auth0_email, original_email):
        return redirect("/join/invitation-sent")
    return render_template("pages/errors/500.html")


def user_is_valid(auth0_email, original_email) -> bool:
    if auth0_email != original_email:
        return False

    if user_email_allowed(auth0_email):
        return True

    return False


def user_email_allowed(email) -> bool:
    domain = email[email.index("@") + 1:]
    if domain in ALLOWED_EMAIL_DOMAINS:
        return True
    return False
