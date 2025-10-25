from flask import Blueprint

# main views blueprint
main = Blueprint('main', __name__)

# home
@main.route('/')
def index():
    return "<h1>Server is running!</h1><p>Ready for the next stage.</p>"