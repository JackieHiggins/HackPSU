from flask import Flask
from config import Config
from .extensions import db
from flask_login import LoginManager

def create_app(config_class=Config):
    # flask instance
    app = Flask(__name__)
    
    # looad config
    app.config.from_object(config_class)

    # register view blueprint 
    from .main_views import main as main_blueprint # Import the main blueprint from main_views.py
    app.register_blueprint(main_blueprint) # Register the main blueprint with the Flask app


    # initialize database
    db.init_app(app)
    # Create the database tables if they don't exist
    with app.app_context():
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

    return app