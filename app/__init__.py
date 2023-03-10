import os

from dotenv import load_dotenv
from flask import Flask

from app.extensions import db, login_manager, mail, migrate


dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(dotenv_path=dotenv_path, verbose=True)


def create_app():
    application = Flask(__name__)
    application.config.from_object("config.DevConfig")

    db.init_app(application)

    login_manager.init_app(application)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."

    mail.init_app(application)
    migrate.init_app(application, db)

    # register blueprints
    from app.auth import auth_blueprint
    from app.errors import errors_blueprint
    from app.main import main_blueprint

    application.register_blueprint(auth_blueprint, url_prefix="/auth")
    application.register_blueprint(errors_blueprint)
    application.register_blueprint(main_blueprint)

    return application
