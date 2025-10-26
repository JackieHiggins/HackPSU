from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from .models import DailyEmoji, Story, User
from .extensions import db
from datetime import date

main = Blueprint('main', __name__)

def get_or_create_daily_prompt():
    """
    Gets today's prompt. If one doesn't exist, it creates a default
    'question mark' prompt for development.
    """
    today = date.today()
    daily_emojis_obj = DailyEmoji.query.filter_by(date_posted=today).first()
    
    if not daily_emojis_obj:
        # No prompt for today, create a placeholder
        default_emojis = "❓ ❓ ❓ ❓ ❓ ❓"
        daily_emojis_obj = DailyEmoji(emojis=default_emojis, date_posted=today)
        db.session.add(daily_emojis_obj)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback() # Handle case where it was created in another request
            print(f"Error creating prompt: {e}")
            daily_emojis_obj = DailyEmoji.query.filter_by(date_posted=today).first()

    return daily_emojis_obj

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    daily_emojis_obj = get_or_create_daily_prompt()
    # Split the emoji string into a list for the homepage template
    emojis = daily_emojis_obj.emojis.split() 
    
    return render_template('base.html', emojis=emojis)

@main.route('/dashboard')
@login_required
def dashboard():
    daily_emojis_obj = get_or_create_daily_prompt()
    
    # Find if the current user has already posted a story for this prompt
    user_story_for_today = Story.query.filter_by(
        author=current_user, 
        daily_emoji_id=daily_emojis_obj.id
    ).first()
        
    return render_template('dashboard.html', 
                           emojis=daily_emojis_obj.emojis, # Pass the full emoji string
                           user_story=user_story_for_today) # Pass the story object (or None)


# --- NEW ROUTES FOR SUBMITTING AND VIEWING ---

@main.route('/submit', methods=['POST'])
@login_required
def submit_story():
    story_content = request.form.get('story_content')
    daily_emojis_obj = get_or_create_daily_prompt() # Get the same prompt object

    if not story_content or len(story_content) < 10:
        flash("Your story must be at least 10 characters long.", "warning")
        return redirect(url_for('main.dashboard'))

    # Check if user can post today
    if not current_user.can_post_today():
        flash("You have already submitted a story for today.", "warning")
        return redirect(url_for('main.dashboard'))

    # Create the new story and link it to the prompt
    try:
        new_story = Story(content=story_content, 
                        author=current_user, 
                        daily_emoji_id=daily_emojis_obj.id)
        db.session.add(new_story)
        # The streak is updated in Story.__init__, now we just need to commit
        db.session.commit()
        flash(f"Story submitted! Your current streak: {current_user.current_streak} days!", "success")
        return redirect(url_for('main.stories')) # Redirect to the stories page
    except Exception as e:
        db.session.rollback()
        flash("Error submitting your story. Please try again.", "error")
        return redirect(url_for('main.dashboard'))


@main.route('/stories')
@login_required
def stories():
    daily_emojis_obj = get_or_create_daily_prompt()
    
    # Your project rule: user must post before they can view stories
    user_story_for_today = Story.query.filter_by( # Check if the current user has already posted a story for this prompt
        author=current_user, 
        daily_emoji_id=daily_emojis_obj.id
    ).first()

    if not user_story_for_today: # If they haven't posted, redirect them back to the dashboard with a message
        flash("You must post your own story before you can view others'.", "warning")
        return redirect(url_for('main.dashboard'))

    # If they passed the check, get all stories for the prompt
    all_stories = Story.query.filter_by(daily_emoji_id=daily_emojis_obj.id).order_by(Story.timestamp.desc()).all() # Get all stories for the current prompt, ordered by most recent
    
    # Render your (currently empty) stories.html file and pass the data to it
    # We will style this file in the next step.
    return render_template('stories.html', 
                           stories=all_stories, 
                           prompt_emojis=daily_emojis_obj.emojis)

