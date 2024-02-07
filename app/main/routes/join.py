import logging
from typing import Any

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.app_config import app_config
from app.main.middleware.auth import requires_auth
from app.main.validators.index import is_valid_email_pattern

logger = logging.getLogger(__name__)
join_route = Blueprint("join_route", __name__)


@join_route.route("/submit-email", methods=["GET", "POST"])
def submit_email():
    if request.method == "POST":
        user_input_email = request.form.get("emailAddress", "Empty").strip()
        if not is_valid_email_pattern(user_input_email):
            flash("Please enter a valid email address.")
            return render_template("pages/submit-email.html")
        session["user_input_email"] = user_input_email
        domain = session["user_input_email"].split("@")[1]
        if domain in set(app_config.github.allowed_email_domains):
            return redirect("/join/select-organisations")
        else:
            return redirect("/join/outside-collaborator")
    return render_template("pages/submit-email.html")


@join_route.route("/outside-collaborator")
def outside_collaborator():
    return render_template(
        "pages/outside-collaborator.html",
        email=session["user_input_email"],
    )


@join_route.route("/select-organisations", methods=["GET", "POST"])
def select_organisations():
    user_input_email = session.get("user_input_email", "").lower()
    domain = user_input_email[user_input_email.index("@") + 1 :]
    is_digital_justice_user = is_digital_justice_email(domain)

    checkboxes_items = [
        {
            "value": org.name,
            "text": org.display_text,
            "disabled": True
            if org.name == "moj-analytical-services" and is_digital_justice_user
            else False,
        }
        for org in get_enabled_organisations()
    ]

    if request.method == "POST":
        sanitised_org_selection = sanitise_org_selection(
            request.form.getlist("organisation_selection")
        )

        if not sanitised_org_selection:
            flash("Please select at least one organisation.")
            return render_template(
                "pages/select-organisations.html",
                checkboxes_items=checkboxes_items,
                is_digital_justice_user=is_digital_justice_user,
            )

        session["org_selection"] = sanitised_org_selection
        return redirect("/join/selection")

    return render_template(
        "pages/select-organisations.html",
        checkboxes_items=checkboxes_items,
        is_digital_justice_user=is_digital_justice_user,
    )


@join_route.route("/selection")
def join_selection():
    user_input_email = session.get("user_input_email", "").lower()
    domain = user_input_email[user_input_email.index("@") + 1 :]
    org_selection = session.get("org_selection", [])

    if is_justice_email(domain):
        template = "pages/justice-user.html"
    elif is_digital_justice_email(domain):
        template = "pages/digital-justice-user.html"
    else:
        template = "pages/join-selection.html"
    return render_template(
        template, org_selection=org_selection, email=user_input_email
    )


@requires_auth
@join_route.route("/invitation-sent")
def invitation_sent():
    auth0_email = session["user"]["userinfo"]["email"].lower()
    org_selection = sanitise_org_selection(session["org_selection"])
    if len(org_selection) == 1:
        org_selection_string = org_selection[0]
        template = "pages/invitation-sent.html"
    else:
        org_selection_string = (
            f"{', '.join(org_selection[:-1])} and {org_selection[-1]}"
        )
        template = "pages/multiple-invitations-sent.html"

    session.clear()

    return render_template(
        template, org_selection_string=org_selection_string, email=auth0_email
    )


@requires_auth
@join_route.route("/send-invitation")
def send_invitation():
    auth0_email = session["user"]["userinfo"]["email"]
    user_input_email = session["user_input_email"]
    org_selection = sanitise_org_selection(session["org_selection"])

    if user_input_email.lower() != auth0_email.lower():
        abort(400, "Users initial email does not match authenticated email")

    if not is_pre_approved_email_domain(auth0_email):
        abort(400, "Users email domain is not pre-approved")

    current_app.github_service.send_invites_to_user_email(auth0_email, org_selection)

    return redirect(url_for("join_route.invitation_sent"))


def get_enabled_organisations() -> list[Any]:
    return [
        organisation
        for organisation in app_config.github.organisations
        if organisation.enabled
    ]


def get_enabled_organisations_names() -> list[str]:
    return [
        organisation.name
        for organisation in app_config.github.organisations
        if organisation.enabled
    ]


def sanitise_org_selection(org_selection: list[str]) -> list[str]:
    enabled_organisation_names = get_enabled_organisations_names()

    sanitised_org_selection = []
    for org_name in org_selection:
        if org_name in enabled_organisation_names:
            sanitised_org_selection.append(org_name)
        else:
            logger.warn(
                f"Organisation [ {org_name} ] is not enabled for selection and has been filtered out"
            )

    return sanitised_org_selection


def is_pre_approved_email_domain(email: str) -> bool:
    domain = email[email.index("@") + 1 :]
    return True if domain in app_config.github.allowed_email_domains else False


def is_digital_justice_email(domain: str) -> bool:
    return "digital.justice.gov.uk" == domain.lower()


def is_justice_email(domain: str) -> bool:
    return "justice.gov.uk" == domain.lower()
