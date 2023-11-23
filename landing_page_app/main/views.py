import os
import logging
from functools import wraps
from urllib.parse import quote_plus, urlencode
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    current_app,
    session,
    url_for,
)
from authlib.integrations.flask_client import OAuth
from github import GithubException

from landing_page_app.main.scripts.join_github_form_auth0_user import (
    JoinGithubFormAuth0User,
)
from landing_page_app.main.config.constants import (
    MINISTRY_OF_JUSTICE,
    MOJ_ANALYTICAL_SERVICES,
    MOJ_ORGS,
    MOJ_ORG_ALLOWED_EMAIL_DOMAINS,
    AS_ORG_ALLOWED_EMAIL_DOMAINS,
)

logger = logging.getLogger(__name__)

AUTHLIB_CLIENT = "authlib.integrations.flask_client"

main = Blueprint("main", __name__)


@main.record
def setup_auth0(setup_state):
    """This is a Blueprint function that is called during app.register_blueprint(main)
    Use this function to set up Auth0

    Args:
        setup_state (Flask): The Flask app itself
    """
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


def requires_auth(function_f):
    """Redirects the web page to /index if user is not logged in

    Args:
        function_f: The calling function

    Returns:
        A redirect to /index or continue with the function that was called
    """

    @wraps(function_f)
    def decorated(*args, **kwargs):
        logger.debug("requires_auth()")
        if "user" not in session:
            return redirect("/index")
        return function_f(*args, **kwargs)

    return decorated


@main.route("/login")
def login():
    """When click on the login button connect to Auth0

    Returns:
        Creates a redirect to /callback if succesful
    """
    logger.debug("login()")
    auth0 = current_app.extensions.get(AUTHLIB_CLIENT)
    return auth0.auth0.authorize_redirect(
        redirect_uri=url_for("main.callback", _external=True)
    )


@main.route("/logout", methods=["GET", "POST"])
def logout():
    """When click on the logout button, clear the session, and log out of Auth0

    Returns:
        Redirects to /index
    """
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


@main.route("/callback", methods=["GET", "POST"])
def callback():
    """If login succesful redirect to /thank-you

    Returns:
        Redirects to /join-github-auth0-user if user has correct email domain else redirects to /logout
    """
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
            allowed_on_moj_org = any(email_address.endswith(domain) for domain in MOJ_ORG_ALLOWED_EMAIL_DOMAINS)
        if organisation.lower() == MOJ_ANALYTICAL_SERVICES:
            allowed_on_as_org = any(email_address.endswith(domain) for domain in AS_ORG_ALLOWED_EMAIL_DOMAINS)
    return bool(allowed_on_moj_org) or bool(allowed_on_as_org)


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


def error(error_message):
    logger.error(error_message)
    return render_template("internal-error.html", error_message=error_message)


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
        "join-github-auth0-user.html", form=form, template="join-github-auth0-user.html"
    )


@main.route("/join-github-auth0-user.html", methods=["GET", "POST"])
@main.route("/join-github-auth0-user", methods=["GET", "POST"])
@requires_auth
def join_github_auth0_users():
    return _join_github_auth0_users(request)


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
    logger.error("A request was made to a page that doesn't exist %s", err)
    return render_template("404.html"), 404


@main.errorhandler(403)
def server_forbidden(err):
    """Load 403.html when server forbids error occurs

    Args:
        err : N/A

    Returns:
        Load the templates/403.html page
    """
    logger.error("server_forbidden(): %s", err)
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
