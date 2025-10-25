from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from .models import DailyEmoji, Story
from datetime import date

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Logic for the public landing page
    today = date.today()
    daily_emojis = DailyEmoji.query.filter_by(date_posted=today).first()
    emojis = daily_emojis.emojis.split() if daily_emojis else ['🌟', '🎨', '🌈', '🚀', '🎭', '✨']
    
    return render_template('base.html', emojis=emojis)

@main.route('/dashboard')
@login_required
def dashboard():
    # Logic for the main user dashboard
    today = date.today()
    daily_emojis = DailyEmoji.query.filter_by(date_posted=today).first()
    emojis = daily_emojis.emojis if daily_emojis else "❓❓❓❓❓❓"
    
    stories = []
    if daily_emojis:
        stories = Story.query.filter_by(daily_emoji_id=daily_emojis.id).order_by(Story.timestamp.desc()).all()
        
    return render_template('dashboard.html', emojis=emojis, posts=stories)