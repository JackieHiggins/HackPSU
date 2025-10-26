from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from .models import User
import re

class RegistrationForm(FlaskForm):
    # at least 8 chars, contains a digit, a special char, a lowercase and an uppercase letter
    passReq = re.compile(r'^(?=.*\d)(?=.*[^A-Za-z0-9])(?=.*[a-z])(?=.*[A-Z]).{8,}$')

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit_register = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate_password(self, password):
        # use match() so the anchored regex is applied to the full string
        if not self.passReq.match(password.data or ''):
            print('Password must meet the requirements.')
            raise ValidationError('Password must meet the requirements.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit_login = SubmitField('Sign In')