from flask import (
    Blueprint,
    render_template
)

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("pages/home.html")


@main.route("/oh_no")
def oh_no():
    1 / 0
    return "<p>Oh no!</p>"
