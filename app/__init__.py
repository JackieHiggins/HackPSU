from flask import Flask
from config import Config

def create_app(config_class=Config):
    # flask instance
    app = Flask(__name__)
    
    # looad config
    app.config.from_object(config_class)

    # register view blueprint 
    from .main_views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app