import logging
from flask import Blueprint, render_template, request, redirect, current_app
from github import GithubException

from landing_page_app.main.scripts.join_github_form import JoinGithubForm

logger = logging.getLogger(__name__)

main = Blueprint("main", __name__)


@main.route("/home")
@main.route("/index")
@main.route("/")
def index():
    """Entrypoint into the application"""
    return render_template("home.html")


@main.route("/join-github.html")
def join_github_info_page():
    return render_template("join-github.html")


@main.route("/thank-you")
def thank_you():
    return render_template("thank-you.html")


@main.route("/use-slack")
def use_slack():
    return render_template("use-slack.html")


@main.route("/use-slack-rejoin-org")
def use_slack_rejoin_org():
    return render_template("use-slack-rejoin-org.html")


def error(error_message):
    logger.error(error_message)
    return render_template("internal-error.html", error_message=error_message)


@main.route("/join-github-form.html", methods=["GET", "POST"])
@main.route("/join-github-form", methods=["GET", "POST"])
def completed_join_github_form():
    form = JoinGithubForm(request.form)
    if request.method == "POST" and form.validate() and form.validate_org():
        selected_orgs = current_app.github_script.get_selected_organisations(
            form.access_moj_org.data, form.access_as_org.data
        )

        if current_app.github_script.is_github_seat_protection_enabled() is True:
            return error("GitHub Seat protection enabled")

        if form.is_user_rejoining_org.data is False:
            non_approved_requests = current_app.github_script.add_new_user_to_github_org(
                form.gh_username.data, form.email_address.data, selected_orgs
            )

            if len(non_approved_requests) == 0:
                # Approved email address. Invite sent to user
                return redirect("thank-you")

            # Non approved email address. Slack alert created
            current_app.slack_service.send_add_new_user_to_github_orgs(
                non_approved_requests
            )

            return redirect("use-slack")

        if form.validate_user_rejoining_org(form.gh_username.data, selected_orgs):
            # User re-joining. Slack alert created
            current_app.slack_service.send_user_wants_to_rejoin_github_orgs(
                form.gh_username.data, form.email_address.data, selected_orgs
            )

            return redirect("use-slack-rejoin-org")

    # Problem in the form
    return render_template(
        "join-github-form.html", form=form, template="join-github-form.html"
    )


@main.errorhandler(GithubException)
def handle_github_exception(error_message):
    logger.error("GitHub exception occurred: %s", error_message)
    return render_template("internal-error.html", error_message=error_message)


@main.errorhandler(404)
def page_not_found(err):
    """Load 404.html when page not found error occurs

    Args:
        err : N/A

    Returns:
        Load the templates/404.html page
    """
    logger.debug("A request was made to a page that doesn't exist %s", err)
    return render_template("404.html"), 404


@main.errorhandler(403)
def server_forbidden(err):
    """Load 403.html when server forbids error occurs

    Args:
        err : N/A

    Returns:
        Load the templates/403.html page
    """
    logger.debug("server_forbidden(): %s", err)
    return render_template("403.html"), 403


@main.errorhandler(500)
def unknown_server_error(err):
    """Load 500.html when unknown server error occurs

    Args:
        err : N/A

    Returns:
        Load the templates/500.html page
    """
    logger.error("An unknown server error occurred: %s", err)
    return render_template("500.html"), 500


@main.errorhandler(504)
def gateway_timeout(err):
    """Load 504.html when gateway timeout error occurs

    Args:
        err : N/A

    Returns:
        Load the templates/504.html page
    """
    logger.error("A gateway timeout error occurred: %s", err)
    return render_template("504.html"), 504
