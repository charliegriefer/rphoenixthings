import os
import logging
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")


load_dotenv(dotenv_path=dotenv_path, verbose=True)

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    SECRET_KEY = os.environ["SECRET_KEY"]
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

    # DATABASE
    SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # MAIL
    MAIL_SERVER = os.environ["MAIL_SERVER"]
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ["MAIL_USERNAME"]
    MAIL_PASSWORD = os.environ["MAIL_PASSWORD"]
    MAIL_SUBJECT_PREFIX = ""
    MAIL_SENDER = "r/Phoenix Mods <mods@rphoenix.xyz>"
    MAIL_ADMINS = ["mods@rphoenix.xyz.", "charlie@griefer.com"]
    MAIL_DEBUG = 1

    # LOGGING
    LOG_LEVEL = logging.DEBUG
    LOG_BACKTRACE = False

    @staticmethod
    def init_app(app):
        pass


class DevConfig(BaseConfig):
    DEBUG = os.environ["DEBUG"]


class ProdConfig(BaseConfig):
    # DATABASE
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # MAIL
    MAIL_DEBUG = 0

    # LOGGING
    LOG_LEVEL = logging.INFO
    LOG_BACKTRACE = True
