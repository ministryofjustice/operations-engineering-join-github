import logging
import os
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from flask import Blueprint, current_app, redirect, render_template, session, url_for

from landing_page_app.main.config.constants import (
    AS_ORG_ALLOWED_EMAIL_DOMAINS,
    MINISTRY_OF_JUSTICE,
    MOJ_ANALYTICAL_SERVICES,
    MOJ_ORG_ALLOWED_EMAIL_DOMAINS,
    MOJ_ORGS,
)

logger = logging.getLogger(__name__)

AUTHLIB_CLIENT = "authlib.integrations.flask_client"

auth_route = Blueprint("auth_routes", __name__)


@auth_route.record
def setup_auth0(setup_state):
    app = setup_state.app
    OAuth(app)
    auth0 = app.extensions.get(AUTHLIB_CLIENT)
    auth0.register(
        "auth0",
        client_id=os.getenv("AUTH0_CLIENT_ID"),
        client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
        client_kwargs={
            "scope": "openid profile email",
        },
        server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/'
        + ".well-known/openid-configuration",
    )


@auth_route.route("/login")
def login():
    logger.debug("login()")
    auth0 = current_app.extensions.get(AUTHLIB_CLIENT)
    return auth0.auth0.authorize_redirect(
        redirect_uri=url_for("auth_routes.callback", _external=True, _scheme="https")
    )


@auth_route.route("/logout", methods=["GET", "POST"])
def logout():
    logger.debug("logout()")
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
        auth0 = current_app.extensions.get(AUTHLIB_CLIENT)
        token = auth0.auth0.authorize_access_token()
        session["user"] = token
    except (KeyError, AttributeError):
        return render_template("500.html"), 500

    try:
        user_email = session["user"]["userinfo"]["email"]
    except KeyError:
        logger.error("Unauthorised: User does not have an email address")
        return render_template("500.html"), 500
    if user_email is None:
        logger.error("User %s does not have an email address", user_email)
        return redirect("/logout")

    if _user_has_approved_auth0_email_address(user_email):
        logger.debug("User %s has approved email domain", user_email)
        return redirect("/join-github-auth0-user")

    logger.error("User %s does not have an approved email domain", user_email)
    return redirect("/logout")


def _user_has_approved_auth0_email_address(email_address):
    allowed_on_moj_org = False
    allowed_on_as_org = False
    for organisation in MOJ_ORGS:
        if organisation.lower() == MINISTRY_OF_JUSTICE:
            allowed_on_moj_org = any(
                email_address.endswith(domain)
                for domain in MOJ_ORG_ALLOWED_EMAIL_DOMAINS
            )
        if organisation.lower() == MOJ_ANALYTICAL_SERVICES:
            allowed_on_as_org = any(
                email_address.endswith(domain)
                for domain in AS_ORG_ALLOWED_EMAIL_DOMAINS
            )
    return bool(allowed_on_moj_org) or bool(allowed_on_as_org)
