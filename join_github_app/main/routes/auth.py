import logging
import os
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from flask import (Blueprint, current_app, redirect, render_template, session,
                   url_for)

from join_github_app.main.config.constants import (
    AS_ORG_ALLOWED_EMAIL_DOMAINS, MINISTRY_OF_JUSTICE, MOJ_ANALYTICAL_SERVICES,
    MOJ_ORG_ALLOWED_EMAIL_DOMAINS, MOJ_ORGS)
from join_github_app.main.validators.join_github_form_auth0_user import \
    JoinGithubFormAuth0User

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

    try:
        user_email = session["user"]["userinfo"]["email"]
    except KeyError:
        logger.error("Unauthorised: User does not have an email address")
        return render_template("pages/errors/500.html"), 500
    if user_email is None:
        logger.error("User %s does not have an email address", user_email)
        return redirect("/auth/logout")

    if _user_has_approved_auth0_email_address(user_email):
        logger.debug("User %s has approved email domain", user_email)
        return redirect("/join/github-auth0-user")

    logger.error("User %s does not have an approved email domain", user_email)
    return redirect("/auth/logout")


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


def _join_github_auth0_users(request):
    form = JoinGithubFormAuth0User(request.form)
    if request.method == "POST" and form.validate() and form.validate_org():
        selected_orgs = current_app.github_script.get_selected_organisations(
            form.access_moj_org.data, form.access_as_org.data
        )

        if current_app.github_script.is_github_seat_protection_enabled() is True:
            return error("GitHub Seat protection enabled")
        else:
            user_email = session["user"]["userinfo"]["email"]
            current_app.github_script.add_new_user_to_github_org(
                user_email, selected_orgs
            )

        return redirect("thank-you")

    # Problem in the form
    return render_template(
        "pages/join-github-auth0-user.html",
        form=form,
        template="join-github-auth0-user.html",
    )
