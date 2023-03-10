from app.main import main_blueprint
from flask_login import current_user, login_required
from flask import current_app, flash, make_response, redirect, render_template, request, url_for
from app.models import User


@main_blueprint.route("/")
@main_blueprint.route("/index")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    return render_template("index.html")


@main_blueprint.route("/home", endpoint="home")
@login_required
def home():
    return render_template("home.html")
