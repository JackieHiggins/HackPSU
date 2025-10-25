from flask import Blueprint, render_template

# main views blueprint
main = Blueprint('main', __name__)

# home
@main.route('/')
def index():
    return render_template('dashboard.html')  

@main.route('/login')
def login():
    return render_template('login.html')