from flask import Flask
from config import Config
from .extensions import db, login_manager
from .models import User
from .extensions import db
from flask_login import LoginManager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- INITIALIZE EXTENSIONS ---
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login_register'
    login_manager.login_message_category = 'info'

    # --- REGISTER BLUEPRINTS ---
    from .main_views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth_views import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # --- FLASK-LOGIN USER LOADER ---
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- CREATE DATABASE TABLES ---
    with app.app_context():
        db.create_all()

    return app
