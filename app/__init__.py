from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
from flask_mail import Mail

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
mail = Mail()
moment = Moment()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp)

    from app.analytics import bp as analytics_bp
    app.register_blueprint(analytics_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.help import bp as help_bp
    app.register_blueprint(help_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.payment import bp as payment_bp
    app.register_blueprint(payment_bp)

    from app.blog import bp as blog_bp
    app.register_blueprint(blog_bp)

    return app

from app import models