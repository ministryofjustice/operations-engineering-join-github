import logging
import re

from flask import Blueprint, current_app, redirect, render_template, request, session, flash

from landing_page_app.main.middleware.auth import requires_auth
from landing_page_app.main.scripts.join_github_form_auth0_user import (
    JoinGithubFormAuth0User,
)

from landing_page_app.main.config.constants import (
    MOJ_ORG_ALLOWED_EMAIL_DOMAINS,
    AS_ORG_ALLOWED_EMAIL_DOMAINS,
    MOJ_ORGS,
)

logger = logging.getLogger(__name__)

AUTHLIB_CLIENT = "authlib.integrations.flask_client"

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("pages/home.html")


@main.route("/join-github")
def join_github_info_page():
    return render_template("pages/join-github.html")


@main.route("/check-email-address", methods=['POST'])
def check_email_address():
    email = request.form.get('emailAddress').strip()
    if len(email.split("@")) != 2:
        # # flash message not working
        # flash("Please enter a valid email address.")
        # return redirect(request.url)
        return render_template("pages/join-github.html")
    else:
        domain = email.split("@")[1]
        if domain not in set(
            MOJ_ORG_ALLOWED_EMAIL_DOMAINS + AS_ORG_ALLOWED_EMAIL_DOMAINS
        ):
            return render_template(
                "pages/external-collaborator.html",
                email=email,
            )
        elif (
            domain in MOJ_ORG_ALLOWED_EMAIL_DOMAINS
            and domain in AS_ORG_ALLOWED_EMAIL_DOMAINS
        ):
            return render_template(
                "pages/join-both-moj-and-as-option.html",
                email=email
            )
        elif (
            domain in MOJ_ORG_ALLOWED_EMAIL_DOMAINS
            and domain not in AS_ORG_ALLOWED_EMAIL_DOMAINS
        ):
            return render_template(
                "pages/join-moj-only-option.html",
                email=email
            )
        elif (
            domain in AS_ORG_ALLOWED_EMAIL_DOMAINS
            and domain not in MOJ_ORG_ALLOWED_EMAIL_DOMAINS
        ):
            return render_template(
                "pages/join-as-only-option.html",
                email=email
            )


@main.route("/thank-you")
def thank_you():
    return render_template("pages/thank-you.html")


def error(error_message):
    logger.error(error_message)
    return render_template(
        "pages/errors/internal-error.html", error_message=error_message
    )


def _join_github_auth0_users(request):
    form = JoinGithubFormAuth0User(request.form)
    if request.method == "POST" and form.validate() and form.validate_org():
        selected_orgs = current_app.github_script.get_selected_organisations(
            form.access_moj_org.data, form.access_as_org.data
        )

        if current_app.github_script.is_github_seat_protection_enabled() is True:
            return error("GitHub Seat protection enabled")

        username = form.gh_username.data
        if len(username) > 0:
            if current_app.github_script.validate_user_rejoining_org(
                selected_orgs, username
            ):
                current_app.github_script.add_returning_user_to_github_org(
                    username, selected_orgs
                )
            else:
                return error(
                    "Username not found or has expired. Create a new request and leave the username box empty."
                )
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


@main.route("/join-github-auth0-user", methods=["GET", "POST"])
@requires_auth
def join_github_auth0_users():
    return _join_github_auth0_users(request)
