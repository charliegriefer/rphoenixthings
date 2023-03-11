from flask import redirect, render_template, url_for
from flask_login import current_user, login_required

from app.main import main_blueprint


@main_blueprint.route("/")
@main_blueprint.route("/index")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    return redirect(url_for("auth.login"))


@main_blueprint.route("/home", endpoint="home")
@login_required
def home():
    return render_template("home.html")
