from flask import Flask
from config import Config
from .extensions import db, login_manager
from .models import User

from dotenv import load_dotenv
load_dotenv()

from flask_login import current_user

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login_register'
    login_manager.login_message_category = 'info'

    from .main_views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth_views import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # --- FLASK-LOGIN USER LOADER ---
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- Provide streak to all templates ---
    @app.context_processor
    def inject_streak():
        return {'current_streak': current_user.current_streak if current_user.is_authenticated else 0}

    # --- CREATE DATABASE TABLES ---
    with app.app_context():
        db.create_all()
    return app
