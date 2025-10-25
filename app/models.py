from .extensions import db
from datetime import datetime

# The User model represents the 'user' table in the database.
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))

class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.String, nullable=False)
    created = db.Column(db.timestamp, nullable=False)
    likes = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Integer, nullable=False)

class Comments(db.Model):
    id = db.Column(db.Interger, primary_key=True)
    message_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    content = db.Column(db.String, nullable=False)
    created = db.Column(db.timestamp, nullable=False)
    likes = db.Column(db.Integer, nullable=False)


