import logging
from flask import Blueprint, render_template, request, redirect, current_app
from github import GithubException

logger = logging.getLogger(__name__)

main = Blueprint("main", __name__)

AUTHLIB_CLIENT = "authlib.integrations.flask_client"


@main.route("/home")
@main.route("/index")
@main.route("/")
def index():
    '''Entrypoint into the application'''
    return render_template("home.html")


@main.route("/join-github.html")
def join_github_info_page():
    return render_template("join-github.html")


@main.route("/join-github-form.html")
def join_github_form():
    return render_template("/join-github-form.html")


@main.route("/thank-you")
def thank_you():
    return render_template("thank-you.html")


@main.route("/form-error")
def form_error():
    return render_template("form-error.html")


@main.route("/completed-join-github-form-handler", methods=['POST'])
def completed_join_github_form():
    gh_username = request.form.get("githubUsername")
    name = request.form.get("userName")
    email_address = request.form.get("userEmailAddress")
    access_moj_org = request.form.get("mojOrgAccess")
    access_as_org = request.form.get("asOrgAccess")

    if gh_username == "" or gh_username is None or name == "" or name is None or email_address == "" or email_address is None:
        return redirect("form-error")

    if access_moj_org is None and access_as_org is None:
        return redirect("form-error")

    current_app.github_script.add_new_user_to_github_org(gh_username, email_address, [access_moj_org, access_as_org])

    return redirect("thank-you")


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
