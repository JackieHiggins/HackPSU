from .extensions import db
from datetime import datetime, date, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    current_streak = db.Column(db.Integer, default=0)  # Current posting streak
    last_story_date = db.Column(db.Date)  # Last date when user posted a story
    
    stories = db.relationship('Story', backref='author', lazy='dynamic')
    comments = db.relationship('Comments', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_streak(self, story_date=None):
        """Update user's streak based on story post date"""
        if story_date is None:
            story_date = date.today()
            
        if not self.last_story_date:
            # First story ever
            self.current_streak = 1
        elif story_date == self.last_story_date:
            # Already posted today, don't update streak
            return
        elif story_date == self.last_story_date + timedelta(days=1):
            # Posted on consecutive day, increment streak
            self.current_streak += 1
        else:
            # Missed a day, reset streak
            self.current_streak = 1
            
        self.last_story_date = story_date

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
    
    def __init__(self, *args, **kwargs):
        super(Story, self).__init__(*args, **kwargs)
        # Update the user's streak when story is created
        if self.author:
            self.author.update_streak(self.timestamp.date())
            db.session.add(self.author)

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    likes = db.Column(db.Integer, nullable=False, default=0)
    
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)