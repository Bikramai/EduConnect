from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

lm = LoginManager()
db = SQLAlchemy()

from .auth import auth
from .main import main
from .teacher import teacher

class Configs:
    SECRET_KEY = "this-is-a-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


def create_app():
    app = Flask(__name__)
    app.config.from_object(Configs)

    lm.init_app(app)
    db.init_app(app)

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(teacher)

    with app.app_context():
        import educonnect.models
        db.create_all()

    return app
