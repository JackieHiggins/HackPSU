from flask import Blueprint, render_template, redirect, url_for
from datetime import date
from .models import DailyEmoji

# main views blueprint
main = Blueprint('main', __name__)

# home
@main.route('/')
def index():
    # Get today's emojis from the database or use defaults
    today = date.today()
    daily_emojis = DailyEmoji.query.filter_by(date_posted=today).first()
    
    # Default emojis if none in database
    emojis = ['🌟', '🎨', '🌈', '🚀', '🎭', '✨']
    if daily_emojis:
        emojis = daily_emojis.emojis.split()
    
    return render_template('base.html', emojis=emojis)

@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@main.route('/login')
def login():
    return render_template('login.html')

@main.route('/logout')
def logout():
    # This will be implemented with proper session handling later
    return redirect(url_for('main.index'))