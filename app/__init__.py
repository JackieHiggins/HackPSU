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
<<<<<<< HEAD
        db.create_all()
=======
        from . import models # Import models to ensure they are registered with SQLAlchemy
        db.create_all() # Create the database tables based on the models defined in models.py

    #Configure Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # User loader function for Flask-Login
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
>>>>>>> ef812f3e8c8748c3e1e620ed5bff9fbbaf5db251

    return app
