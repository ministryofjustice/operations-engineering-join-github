from flask import Flask

from app.main.routes.auth import auth_route
from app.main.routes.join import join_route
from app.main.routes.main import main
from app.main.routes.robots import robot_route


def configure_routes(app: Flask) -> None:
    app.register_blueprint(auth_route, url_prefix="/auth")
    app.register_blueprint(join_route, url_prefix="/join")
    app.register_blueprint(main)
    app.register_blueprint(robot_route)
