from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import current_user, login_required
from .models import DailyEmoji, Story, User, Comments
from .extensions import db
from datetime import date
import random 

main = Blueprint('main', __name__)

# A large, static list of emojis to be used for prompts
EMOJI_POOL = [
    # Smileys & Emotion
    "😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "😊", "😇", "🙂", "🙃", "😉", "😌", "😍", "🥰", "😘", 
    "😗", "😙", "😚", "😋", "😛", "😜", "🤪", "🤨", "🧐", "🤓", "😎", "🤩", "🥳", "😏", "😒", "😞", 
    "😔", "😟", "😕", "🙁", "☹️", "😣", "😖", "😫", "😩", "🥺", "😢", "😭", "😤", "😠", "😡", "🤬", 
    "🤯", "😳", "🥵", "🥶", "😱", "😨", "😰", "😥", "😓", "🤗", "🤔", "🤭", "🤫", "🤥", "😶", "😐", 
    "😑", "😬", "🙄", "😯", "😦", "😧", "😮", "😲", "🥱", "😴", "🤤", "😪", "😵", "🤐", "🥴", "🤢", 
    "🤮", "🤧", "😷", "🤒", "🤕", "🤑", "🤠", "😈", "👿", "👹", "👺", "🤡", "💩", "👻", "💀", "☠️", 
    "👽", "👾", "🤖", "🎃", "😺", "😸", "😹", "😻", "😼", "😽", "🙀", "😿", "😾",
    # People & Body
    "👋", "🤚", "🖐️", "✋", "🖖", "👌", "🤌", "🤏", "✌️", "🤞", "🤟", "🤘", "🤙", "👈", "👉", "👆", "🖕", 
    "👇", "☝️", "👍", "👎", "✊", "👊", "🤛", "🤜", "👏", "🙌", "👐", "🤲", "🤝", "🙏", "✍️", "💅", 
    "🤳", "💪", "🦾", "🦵", "🦿", "🦶", "👣", "👀", "👁️", "🧠", "🫀", "🫁", "🦷", "🦴", "👅", "👄",
    # Animals & Nature
    "🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐻‍❄️", "🐨", "🐯", "🦁", "🐮", "🐷", "🐸", "🐵", 
    "🐔", "🐧", "🐦", "🐤", "🦆", "🦅", "🦉", "🦇", "🐺", "🐗", "🐴", "🦄", "🐝", "🐛", "🦋", "🐌", 
    "🐞", "🐜", "🦟", "🦗", "🕷️", "🦂", "🐢", "🐍", "🦎", "🦖", "🦕", "🐙", "🦑", "🦐", "🦞", "🦀", 
    "🐡", "🐠", "🐟", "🐬", "🐳", "🐋", "🦈", "🐊", "🐅", "🐆", "🦓", "🦍", "🦧", "🐘", "🦛", "🦏", 
    "🐪", "🐫", "🦒", "🦘", "🐃", "🐂", "🐄", "🐎", "🐖", "🐏", "🐑", "🦙", "🐐", "🦌", "🐕", "🐩", 
    "🦮", "🐕‍🦺", "🐈", "🐈‍⬛", "🐓", "🦃", "🦤", "🦚", "🦜", "🦢", "🦩", "🕊️", "🐇", "🦝", "🦨", 
    "🦡", "🦦", "🦥", "🐁", "🐀", "🐿️", "🦔", "🌍", "🌎", "🌏", "🌋", "🏔️", "🏕️", "🏖️", "🏜️", "🏝️", 
    "🏞️", "🏟️", "🏛️", "🏗️", "🧱", "🪨", "🪵", "🛖", "🏘️", "🏚️", "🏠", "🏡", "🏢", "🏣", "🏤", "🏥", 
    "🏦", "🏨", "🏪", "🏫", "🏬", "🏭", "🏯", "🏰", "💒", "🗼", "🗽", "🕌", "🛕", "🕍", "⛩️", "🕋", 
    "⛲", "⛺", "🌁", "🌃", "🏙️", "🌄", "🌅", "🌆", "🌇", "🌉", "🎠", "🎡", "🎢", "🚂", "🚃", "🚄", 
    "🚅", "🚆", "🚇", "🚈", "🚉", "🚊", "🚝", "🚞", "🚋", "🚌", "🚍", "🚎", "🚐", "🚑", "🚒", "🚓", 
    "🚔", "🚕", "🚖", "🚗", "🚘", "🚙", "🛻", "🚚", "🚛", "🚜", "🏎️", "🏍️", "🛵", "🦽", "🦼", "🛺", 
    "🚲", "🛴", "🛹", "🛼", "🛸", "🚁", "🚡", "🚠", "🚟", "✈️", "🚀", "🛰️", "⛵", "🚤", "🛳️", "⛴️", 
    "🚢", "⚓", "⛽", "🚧", "🚦", "🚥", "🛑", "🔥", "✨", "🌟", "💫", "💥", "☄️", "☀️", "🌤️", "⛅", 
    "🌥️", "☁️", "🌦️", "🌧️", "⛈️", "🌩️", "🌨️", "❄️", "☃️", "⛄", "🌬️", "💨", "💧", "💦", "☔", "☂️", 
    "🌊", "🌫️", "🌪️", "🌲", "🌳", "🌴", "🌵", "🌾", "🌿", "🍀", "🍁", "🍂", "🍃",
    # Food & Drink
    "🍇", "🍈", "🍉", "🍊", "🍋", "🍌", "🍍", "🥭", "🍎", "🍏", "🍐", "🍑", "🍒", "🍓", "🫐", "🥝", 
    "🍅", "🫒", "🥥", "🥑", "🍆", "🥔", "🥕", "🌽", "🌶️", "🫑", "🥒", "🥬", "🥦", "🧄", "🧅", "🍄", 
    "🥜", "🌰", "🍞", "🥐", "🥖", "🫓", "🥨", "🥯", "🥞", "🧇", "🧀", "🍖", "🍗", "🥩", "🥓", "🍔", 
    "🍟", "🍕", "🌭", "🥪", "🌮", "🌯", "🫔", "🥙", "🧆", "🥚", "🍳", "🥘", "🍲", "🫕", "🥣", "🥗", 
    "🍿", "🧈", "🧂", "🥫", "🍱", "🍘", "🍙", "🍚", "🍛", "🍜", "🍝", "🍠", "🍢", "🍣", "🍤", "🍥", 
    "🥮", "🍡", "🥟", "🥠", "🥡", "🦀", "🦞", "🦐", "🦑", "🦪", "🍦", "🍧", "🍨", "🍩", "🍪", "🎂", 
    "🍰", "🧁", "🥧", "🍫", "🍬", "🍭", "🍮", "🍯", "🍼", "🥛", "☕", "🫖", "🍵", "🍶", "🍾", "🍷", 
    "🍸", "🍹", "🍺", "🍻", "🥂", "🥃", "🫗", "🥤", "🧋", "🧃", "🧉", "🧊", "🥢", "🍴", "🥄", "🔪",
    # Objects
    
    "💎", "💍", "👑", "🎩", "🎓", "⛑️", "💡", "💰", "💵", "💴", "💶", "💷", "💳", "🔑", "🚪", "🛋️", 
    "🚽", "🚿", "🛁", "🔨", "⛏️", "⚙️", "🔧", "🔩", "🧱", "⛓️", "💣", "🔫", "🔪", "🛡️", "🚬", "⚰️", 
    "🔮", "🧿", "📿", "💈", "⚗️", "🔭", "🔬", "💊", "💉", "🩸", "🩹", "🩺", "🌡️", "⚖️", "📜", "✉️", 
    "📦", "📮", "🗳️", "🗓️", "📆", "📅", "📈", "📉", "📊", "📋", "📌", "📍", "📎", "📏", "📐", "✂️", 
    "🗑️", "🔒", "🔓", "🔏", "🔐", "🔎", "📚", "📖", "🔖", "🏷️", "📰", "🗞️", "🎨", "🎬", "🎤", "🎧", 
    "🎷", "🎸", "🎹", "🎺", "🎻", "🪕", "🥁", "📱", "💻", "🖥️", "🖱️", "💾", "💿", "📀", "🎥", "🎞️", 
    "📽️", "📺", "📷", "📸", "📹", "📼", "🔍", "🔎", "🕯️", "💡", "🔦", "🏮", "🪔", "📔", "📕", "📗", 
    "📘", "📙", "📓", "📒", "📝", "✏️", "✒️", "🖋️", "🖊️", "🖌️", "🖍️", "🖊️", "🖋️",
    # Symbols
    "❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💔", "❣️", "💕", "💞", "💓", "💗", "💖", "💘", 
    "💝", "💟", "☮️", "✝️", "☪️", "🕉️", "☸️", "✡️", "🔯", "🕎", "☯️", "☦️", "🛐", "⛎", "♈", "♉", 
    "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓", "🆔", "⚛️", "🉑", "☢️", "☣️", "📴", "📳", 
    "🈶", "🈚", "🈸", "🈺", "🈷️", "✴️", "🆚", "💮", "🉐", "㊙️", "㊗️", "🈴", "🈵", "🈹", "🈲", "🅰️", 
    "🅱️", "🆎", "🆑", "🅾️", "🆘", "❌", "⭕", "🛑", "⛔", "📛", "🚫", "💯", "💢", "♨️", "🚷", "🚯", 
    "🚳", "🚱", "🔞", "📵", "🚭", "❗", "❕", "❓", "❔", "‼️", "⁉️", "🔅", "🔆", "〽️", "⚠️", "🚸", 
    "🔱", "⚜️", "🔰", "♻️", "✅", "🈯", "💹", "❇️", "✳️", "❎", "🌐", "💠", "Ⓜ️", "🌀", "💤", "🏧", 
    "🚾", "♿", "🅿️", "🛗", "🈳", "🈂️", "🛂", "🛃", "🛄", "🛅", "🚹", "🚺", "🚼", "🚻", "🚮", "🎦", 
    "📶", "🈁", "🔣", "ℹ️", "🔤", "🔡", "🔠", "🆖", "🆗", "🆙", "🆒", "🆕", "🆓", "0️⃣", "1️⃣", "2️⃣", 
    "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟", "🔢", "#️⃣", "*️⃣", "⏏️", "▶️", "⏸️", "⏯️", 
    "⏹️", "⏺️", "⏭️", "⏮️", "⏩", "⏪", "⏫", "⏬", "◀️", "🔼", "🔽", "➡️", "⬅️", "⬆️", "⬇️", "↗️", 
    "↘️", "↙️", "↖️", "↕️", "↔️", "↪️", "↩️", "⤴️", "⤵️", "🔀", "🔁", "🔂", "🔄", "🔃", "🎵", "🎶", 
    "➕", "➖", "➗", "✖️", "♾️", "💲", "💱", "™️", "©️", "®️", "🔚", "🔙", "🔛", "🔝", "🔜", "☑️", 
    "🔘", "🔴", "🟠", "🟡", "🟢", "🔵", "🟣", "🟤", "⚫", "⚪", "🟥", "🟧", "🟨", "🟩", "🟦", "🟪", 
    "🟫", "⬛", "⬜", "◼️", "◻️", "◾", "◽", "▪️", "▫️", "🔶", "🔷", "🔸", "🔹", "🔺", "🔻", "💠", 
    "🔘", "🔳", "🔲"
]

def get_or_create_daily_prompt():
    """
    Gets today's prompt. If one doesn't exist, it creates a random one
    seeded by the date.
    """
    today = date.today()
    daily_emojis_obj = DailyEmoji.query.filter_by(date_posted=today).first()
    
    if not daily_emojis_obj:

        random.seed(today.isoformat())
        
        random_emojis = random.sample(EMOJI_POOL, 6)
        
        emoji_string = " ".join(random_emojis)

        daily_emojis_obj = DailyEmoji(emojis=emoji_string, date_posted=today)
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
    # split the emoji string into a list for the homepage template
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



@main.route('/submit', methods=['POST'])
@login_required
def submit_story():
    story_content = request.form.get('story_content')
    daily_emojis_obj = get_or_create_daily_prompt()

    # Double-check if user already submitted a story for today
    existing_story = Story.query.filter_by(
        author=current_user,
        daily_emoji_id=daily_emojis_obj.id
    ).first()

    if existing_story:
        return redirect(url_for('main.stories'))  # If they already submitted, just go to stories

    if not story_content or len(story_content) < 10:
        flash("Your story must be at least 10 characters long.", "warning")
        return redirect(url_for('main.dashboard'))

    # Create the new story and link it to the prompt
    try:
        new_story = Story(content=story_content,
                          author=current_user,
                          daily_emoji_id=daily_emojis_obj.id)

        # Update the user's streak explicitly here (avoid side-effects in model __init__)
        current_user.update_streak(date.today())

        db.session.add(new_story)
        db.session.add(current_user)
        db.session.commit()
        flash(f"Story submitted! Your current streak: {current_user.current_streak} days!", "success")
        return redirect(url_for('main.stories'))
    except Exception as e:
        db.session.rollback()
        # Log error to console for debugging (do not expose raw error to users)
        print(f"Error committing new story: {e}")
        try:
            import traceback
            traceback.print_exc()
        except Exception:
            pass
        flash("Error submitting your story. Please try again.", "error")
        return redirect(url_for('main.dashboard'))



@main.route('/stories')
@login_required
def stories():
    daily_emojis_obj = get_or_create_daily_prompt()
    
    user_story_for_today = Story.query.filter_by( # Check if the current user has already posted a story for this prompt
        author=current_user, 
        daily_emoji_id=daily_emojis_obj.id
    ).first()

    if not user_story_for_today: # If they haven't posted, redirect them back to the dashboard with a message
        flash("You must post your own story before you can view others'.", "warning")
        return redirect(url_for('main.dashboard'))

    # Get all stories for the prompt ordered by most recent
    all_stories = Story.query.filter_by(daily_emoji_id=daily_emojis_obj.id).order_by(Story.timestamp.desc()).all()

    ordered_stories = []

    # Add current user's story first (use the actual story object to preserve timestamp/content)
    if user_story_for_today:
        ordered_stories.append({
            'id': user_story_for_today.id,
            'username': current_user.username,
            'content': user_story_for_today.content,
            'timestamp': user_story_for_today.timestamp.strftime('%Y-%m-%d %H:%M'),
            'likes': user_story_for_today.likes,
            'is_you': True
        })

    # Add other users' stories (skip the current user's to avoid duplication)
    for story in all_stories:
        if story.user_id == current_user.id:
            continue
        author_name = story.author.username if story.author else 'Unknown'
        ordered_stories.append({
            'id': story.id,
            'username': author_name,
            'content': story.content,
            'timestamp': story.timestamp.strftime('%Y-%m-%d %H:%M'),
            'likes': story.likes,
            'is_you': False
        })

    # liked story ids stored in session so users can toggle their local like state
    liked_stories = session.get('liked_stories', [])

    return render_template('stories.html', 
                           ordered_stories=ordered_stories, 
                           prompt_emojis=daily_emojis_obj.emojis,
                           user_story=user_story_for_today,
                           liked_stories=liked_stories)


@main.route('/stories/<int:story_id>/like', methods=['POST'])
@login_required
def like_story(story_id):
    story = Story.query.get_or_404(story_id)
    # only allow liking stories for the current prompt/day (optional safety)
    daily_emojis_obj = get_or_create_daily_prompt()
    if story.daily_emoji_id != daily_emojis_obj.id:
        return jsonify({'error': 'Invalid story for current prompt.'}), 400

    liked = False
    liked_list = session.get('liked_stories', [])
    if story_id in liked_list:
        # toggle off
        if story.likes > 0:
            story.likes -= 1
        liked_list.remove(story_id)
        liked = False
    else:
        story.likes += 1
        liked_list.append(story_id)
        liked = True

    session['liked_stories'] = liked_list
    try:
        db.session.add(story)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'DB error'}), 500

    return jsonify({'likes': story.likes, 'liked': liked})

@main.route('/profile')
@login_required
def profile():
    # Get the current user's profile information and their stories
    # user_posts: all stories authored by the user (most recent first)
    user_posts = Story.query.filter_by(author=current_user).order_by(Story.timestamp.desc()).all()

    # user_comments: comments made by the user. For each comment include the title/snippet of the story it references
    raw_comments = Comments.query.filter_by(user_id=current_user.id).order_by(Comments.created.desc()).all()
    user_comments = []
    for c in raw_comments:
        # Try to find the story this comment references
        story = None
        if c.story_id:
            story = Story.query.get(c.story_id)
        post_title = story.content[:60] + '...' if story and len(story.content) > 60 else (story.content if story else 'Unknown')
        user_comments.append({
            'post_title': post_title,
            'content': c.content,
            'date_posted': c.created.strftime('%Y-%m-%d %H:%M')
        })

    # user_likes: the UI expects a list of liked posts. We don't have a persistent Like model,
    # so use session['liked_stories'] (client-side) to show what this browser liked.
    liked_ids = session.get('liked_stories', [])
    user_likes = []
    if liked_ids:
        stories = Story.query.filter(Story.id.in_(liked_ids)).all()
        for s in stories:
            user_likes.append({
                'post_title': s.content[:60] + ('...' if len(s.content) > 60 else ''),
                'date_liked': s.timestamp.strftime('%Y-%m-%d %H:%M')
            })

    return render_template('user.html',
                           current_user=current_user,
                           user_posts=user_posts,
                           user_comments=user_comments,
                           user_likes=user_likes)

@main.route('/streak')
@login_required
def streak():
    # Get the current user's streak information
    current_streak = current_user.current_streak

    return render_template('streak.html',
                           current_user=current_user,
                           current_streak=current_streak)

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/stories/<int:story_id>/edit', methods=['POST'])
@login_required
def edit_story(story_id):
    story = Story.query.get_or_404(story_id)
    daily_emojis_obj = get_or_create_daily_prompt()
    # ensure owner and same-day story
    if story.user_id != current_user.id or story.daily_emoji_id != daily_emojis_obj.id:
        flash("You can only edit your own story for today's prompt.", "warning")
        return redirect(url_for('main.stories'))

    new_content = None
    if request.is_json:
        new_content = request.json.get('content', '').strip()
    else:
        new_content = request.form.get('story_content', '').strip()

    if not new_content or len(new_content) < 10:
        flash("Edited story must be at least 10 characters long.", "warning")
        return jsonify({'success': False, 'message': 'Content too short.'}), 400

    story.content = new_content
    try:
        db.session.add(story)
        db.session.commit()
        flash("Your story has been updated.", "success")
        return jsonify({'success': True, 'content': story.content})
    except Exception as e:
        db.session.rollback()
        flash("Error updating your story. Please try again.", "error")
        return jsonify({'success': False}), 500