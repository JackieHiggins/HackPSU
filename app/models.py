from .extensions import db
from datetime import datetime, date

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    
    stories = db.relationship('Story', backref='author', lazy='dynamic')
    comments = db.relationship('Comments', backref='author', lazy='dynamic')

class DailyEmoji(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emojis = db.Column(db.String(50), nullable=False)
    date_posted = db.Column(db.Date, unique=True, nullable=False, default=date.today) 
    stories = db.relationship('Story', backref='daily_emoji_set', lazy='dynamic')

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow) 
    likes = db.Column(db.Integer, nullable=False, default=0)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    daily_emoji_id = db.Column(db.Integer, db.ForeignKey('daily_emoji.id'))
    
    comments = db.relationship('Comments', backref='story', lazy='dynamic')

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    likes = db.Column(db.Integer, nullable=False, default=0)
    
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

