from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from .run import app


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

users_db = {}

@login_manager.user_loader
def load_user(user_id):
    return users_db.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        for user_id, user in users_db.items():
            if user.email == email:
                login_user(user)
                return redirect(url_for('dashboard'))
        return "Invalid email or password"
    return render_template('login.html')