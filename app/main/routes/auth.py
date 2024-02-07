import logging

from flask import Blueprint, current_app, redirect, session, url_for

from app.app_config import app_config
from app.main.services.auth0_service import Auth0_Service

logger = logging.getLogger(__name__)

auth_route = Blueprint("auth_routes", __name__)

auth0_service = Auth0_Service(
    current_app,
    app_config.auth0.client_id,
    app_config.auth0.client_secret,
    app_config.auth0.domain,
)


@auth_route.route("/login")
def login():
    return auth0_service.login(url_for("auth_routes.callback", _external=True))


@auth_route.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    auth0_service.logout(url_for("main.index", _external=True))


@auth_route.route("/callback", methods=["GET", "POST"])
def callback():
    session["user"] = auth0_service.get_access_token()
    return redirect("/join/send-invitation")
