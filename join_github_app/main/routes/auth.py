import logging
import os
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from flask import (Blueprint, current_app, redirect, render_template, session,
                   url_for)

from join_github_app.main.config.constants import ALLOWED_EMAIL_DOMAINS
from join_github_app.main.middleware.error_handler import AuthTokenError

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
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("auth_routes.callback", _external=True)
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
        token = get_token()
        session["user"] = token
    except AuthTokenError:
        return render_error_page()

    if not process_user_session():
        logger.debug("User session processing failed")
        return render_error_page()

    org_selection = session.get("org_selection", [])
    original_email = session.get("email")

    if not send_github_invitation(original_email, org_selection):
        return render_error_page()

    return render_success_page()


def get_token():
    try:
        token = oauth.auth0.authorize_access_token()
        if not token:
            raise AuthTokenError("No token received from Auth0")
        return token
    except Exception as e:
        logger.error("Error retrieving token: %s", e)
        raise AuthTokenError("Error retrieving token from Auth0") from e


def process_user_session():
    """
    Process and validate user session data.

    :return: True if session processing is successful, False otherwise.
    """
    if 'user' not in session or 'email' not in session:
        logger.error("Missing user or email in session")
        return False

    auth0_email = session["user"].get("userinfo", {}).get("email")
    original_email = session["email"]
    org_selection = session.get("org_selection", [])

    if not auth0_email or not user_is_valid(auth0_email, original_email):
        logger.error("Invalid email in session or email mismatch")
        return False

    if not org_selection:
        logger.debug("No organisations selected")
        return False

    return True


def send_github_invitation(email, org_selection):
    """
    Send an invitation to the specified GitHub organization(s).

    :param email: Email of the user to send the invitation to.
    :param org_selection: List of organizations to invite the user to.
    :return: True if the invitation was sent successfully, False otherwise.
    """
    try:
        current_app.github_service.send_invitation_to_organisation(email, org_selection)
        return True
    except Exception as e:
        logger.error("Error sending GitHub invitation: %s", e)
        return False


def render_success_page():
    return render_template("pages/invitation-sent.html")


def render_error_page():
    return render_template("pages/errors/500.html"), 500


def user_is_valid(auth0_email, original_email) -> bool:
    if auth0_email.lower() != original_email.lower():
        return False

    if user_email_allowed(auth0_email):
        return True

    return False


def user_email_allowed(email) -> bool:
    domain = email[email.index("@") + 1:]
    if domain in ALLOWED_EMAIL_DOMAINS:
        return True
    return False
