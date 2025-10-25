from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from .forms import LoginForm, RegistrationForm
from .models import User
from .extensions import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login_register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    login_form = LoginForm()
    reg_form = RegistrationForm()

    if reg_form.submit_register.data and reg_form.validate():
        user = User(username=reg_form.username.data, email=reg_form.email.data)
        user.set_password(reg_form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, your account has been created!', 'success')
        login_user(user)
        return redirect(url_for('main.dashboard'))

    if login_form.submit_login.data and login_form.validate():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user and user.check_password(login_form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html', 
                           title='Login / Register', 
                           login_form=login_form, 
                           reg_form=reg_form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))