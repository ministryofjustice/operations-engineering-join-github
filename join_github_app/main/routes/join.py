from flask import (Blueprint, flash, redirect, render_template,
                   request, session)

from join_github_app.app_config import app_config
from join_github_app.main.validators.index import is_valid_email_pattern

join_route = Blueprint('join_route', __name__)


@join_route.route("/submit-email", methods=["GET", "POST"])
def submit_email():
    if request.method == "POST":
        email = request.form.get("emailAddress", "Empty").strip()
        if not is_valid_email_pattern(email):
            flash("Please enter a valid email address.")
            return render_template("pages/submit-email.html")
        session['email'] = email
        domain = session["email"].split("@")[1]
        if domain in set(app_config.github.allowed_email_domains):
            return redirect("/join/select-organisations")
        else:
            return redirect("/join/outside-collaborator")
    return render_template("pages/submit-email.html")


@join_route.route("/outside-collaborator")
def outside_collaborator():
    return render_template(
        "pages/outside-collaborator.html",
        email=session["email"],
    )


@join_route.route("/select-organisations", methods=["GET", "POST"])
def select_organisations():
    email = session.get("email", "").lower()
    domain = email[email.index("@") + 1:]
    is_digital_justice_user = is_digital_justice_email(domain)
    enabled_organisations = [organisation for organisation in app_config.github.organisations if organisation.enabled]

    checkboxes_items = [{
        "value": org.name,
        "text": org.display_text,
        "disabled": True if org.name == "moj-analytical-services" and is_digital_justice_user else False
    } for org in enabled_organisations]

    if request.method == "POST":
        session["org_selection"] = request.form.getlist("organisation_selection")
        if not session["org_selection"]:
            flash("Please select at least one organisation.")
            return render_template(
                "pages/select-organisations.html",
                checkboxes_items=checkboxes_items,
                is_digital_justice_user=is_digital_justice_user,
            )
        return redirect("/join/selection")

    return render_template(
        "pages/select-organisations.html",
        checkboxes_items=checkboxes_items,
        is_digital_justice_user=is_digital_justice_user,
    )


@join_route.route("/selection")
def join_selection():
    email = session.get("email", "").lower()
    domain = email[email.index("@") + 1:]
    org_selection = session.get("org_selection", [])

    if is_justice_email(domain):
        template = "pages/justice-user.html"
    elif is_digital_justice_email(domain):
        template = "pages/digital-justice-user.html"
    else:
        template = "pages/join-selection.html"
    return render_template(template, org_selection=org_selection, email=email)


@join_route.route("/invitation-sent")
def invitation_sent():
    return render_template("pages/invitation-sent.html")


@join_route.route("/submitted")
def submitted():
    return render_template("pages/thank-you.html")


def is_digital_justice_email(domain):
    return "digital.justice.gov.uk" == domain.lower()


def is_justice_email(domain):
    return "justice.gov.uk" == domain.lower()
