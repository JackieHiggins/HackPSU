from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import current_user, login_required
from .models import DailyEmoji, Story, User, Comments
from .extensions import db
from datetime import date
import random
import os
from werkzeug.utils import secure_filename
import google.generativeai as genai

main = Blueprint('main', __name__)

# initialize Gemini API client if API key is available
try:
    API_KEY = os.environ.get('GEMINI_API_KEY')
    if API_KEY:
        genai.configure(api_key=API_KEY)
        gemini_model = genai.GenerativeModel('gemini-2.5-flash')
        moderation_enabled = True
        print("SUCCESS: Gemini API client initialized.")
    else:
        print("WARNING: GEMINI_API_KEY not found. Moderation is disabled.")
        gemini_model = None
        moderation_enabled = False
except Exception as e:
    print(f"WARNING: Gemini client could not be initialized. Moderation is disabled. Error: {e}")
    gemini_model = None
    moderation_enabled = False

EMOJI_POOL = [
    "😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "😊", "😇", "🙂", "🙃", "😉", "😌", "😍", "🥰", "😘",
    "😗", "😙", "😚", "😋", "😛", "😜", "🤪", "🤨", "🧐", "🤓", "😎", "🤩", "🥳", "😏", "😒", "😞",
    "😔", "😟", "😕", "🙁", "☹️", "😣", "😖", "😫", "😩", "🥺", "😢", "😭", "😤", "😠", "😡", "🤬",
    "🤯", "😳", "🥵", "🥶", "😱", "😨", "😰", "😥", "😓", "🤗", "🤔", "🤭", "🤫", "🤥", "😶", "😐",
    "😑", "😬", "🙄", "😯", "😦", "😧", "😮", "😲", "🥱", "😴", "🤤", "😪", "😵", "🤐", "🥴", "🤢",
    "🤮", "🤧", "😷", "🤒", "🤕", "🤑", "🤠", "😈", "👿", "👹", "👺", "🤡", "💩", "👻", "💀", "☠️",
    "👽", "👾", "🤖", "🎃", "😺", "😸", "😹", "😻", "😼", "😽", "🙀", "😿", "😾", "👋", "🤚", "🖐️", "✋", "🖖", "👌",
    "🤌", "🤏", "✌️", "🤞", "🤟", "🤘", "🤙", "👈", "👉", "👆", "👇", "☝️", "👍", "👎", "✊", "👊", "🤛", "🤜", "👏", "🙌",
    "👐", "🤲", "🤝", "🙏", "✍️", "💅", "🤳", "💪", "🦾", "🦵", "🦿", "🦶", "👣", "👀", "👁️", "🧠", "🫀", "🫁", "🦷",
    "🦴", "👅", "👄", "🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐻‍❄️", "🐨", "🐯", "🦁", "🐮", "🐷", "🐸",
    "🐵", "🐔", "🐧", "🐦", "🐤", "🦆", "🦅", "🦉", "🦇", "🐺", "🐗", "🐴", "🦄", "🐝", "🐛", "🦋", "🐌", "🐞", "🐜",
    "🦟", "🦗", "🕷️", "🦂", "🐢", "🐍", "🦎", "🦖", "🦕", "🐙", "🦑", "🦐", "🦞", "🦀", "🐡", "🐠", "🐟", "🐬", "🐳",
    "🐋", "🦈", "🐊", "🐅", "🐆", "🦓", "🦍", "🦧", "🐘", "🦛", "🦏", "🐪", "🐫", "🦒", "🦘", "🐃", "🐂", "🐄", "🐎",
    "🐖", "🐏", "🐑", "🦙", "🐐", "🦌", "🐕", "🐩", "🦮", "🐕‍🦺", "🐈", "🐈‍⬛", "🐓", "🦃", "🦤", "🦚", "🦜", "🦢",
    "🦩", "🕊️", "🐇", "🦝", "🦨", "🦡", "🦦", "🦥", "🐁", "🐀", "🐿️", "🦔", "🌍", "🌎", "🌏", "🌋", "🏔️", "🏕️",
    "🏖️", "🏜️", "🏝️", "🏞️", "🏟️", "🏛️", "🏗️", "🧱", "🪨", "🪵", "🛖", "🏘️", "🏚️", "🏠", "🏡", "🏢", "🏣", "🏤",
    "🏥", "🏦", "🏨", "🏪", "🏫", "🏬", "🏭", "🏯", "🏰", "💒", "🗼", "🗽", "🕌", "🛕", "🕍", "⛩️", "🕋", "⛲", "⛺",
    "🌁", "🌃", "🏙️", "🌄", "🌅", "🌆", "🌇", "🌉", "🎠", "🎡", "🎢", "🚂", "🚃", "🚄", "🚅", "🚆", "🚇", "🚈", "🚉",
    "🚊", "🚝", "🚞", "🚋", "🚌", "🚍", "🚎", "🚐", "🚑", "🚒", "🚓", "🚔", "🚕", "🚖", "🚗", "🚘", "🚙", "🛻",
    "🚚", "🚛", "🚜", "🏎️", "🏍️", "🛵", "🦽", "🦼", "🛺", "🚲", "🛴", "🛹", "🛼", "🛸", "🚁", "🚡", "🚠", "🚟",
    "✈️", "🚀", "🛰️", "⛵", "🚤", "🛳️", "⛴️", "🚢", "⚓", "⛽", "🚧", "🚦", "🚥", "🛑", "🔥", "✨", "🌟", "💫", "💥",
    "☄️", "☀️", "🌤️", "⛅", "🌥️", "☁️", "🌦️", "🌧️", "⛈️", "🌩️", "🌨️", "❄️", "☃️", "⛄", "🌬️", "💨", "💧", "💦", "☔",
    "☂️", "🌊", "🌫️", "🌪️", "🌲", "🌳", "🌴", "🌵", "🌾", "🌿", "🍀", "🍁", "🍂", "🍃", "🍇", "🍈", "🍉", "🍊", "🍋",
    "🍌", "🍍", "🥭", "🍎", "🍏", "🍐", "🍑", "🍒", "🍓", "🫐", "🥝", "🍅", "🫒", "🥥", "🥑", "🍆", "🥔", "🥕", "🌽",
    "🌶️", "🫑", "🥒", "🥬", "🥦", "🧄", "🧅", "🍄", "🥜", "🌰", "🍞", "🥐", "🥖", "𫓓", "🥨", "🥯", "🥞", "🧇", "🧀",
    "🍖", "🍗", "🥩", "🥓", "🍔", "🍟", "🍕", "🌭", "🥪", "🌮", "🌯", "𫔔", "🥙", "🧆", "🥚", "🍳", "🥘", "🍲", "𫕕",
    "🥣", "🥗", "🍿", "🧈", "🧂", "🥫", "🍱", "🍘", "🍙", "🍚", "🍛", "🍜", "🍝", "🍠", "🍢", "🍣", "🍤", "🍥", "🥮",
    "🍡", "🥟", "🥠", "🥡", "🦀", "🦞", "🦐", "🦑", "🦪", "🍦", "🍧", "🍨", "🍩", "🍪", "🎂", "🍰", "🧁", "🥧", "🍫",
    "🍬", "🍭", "🍮", "🍯", "🍼", "🥛", "☕", "𫖖", "🍵", "🍶", "🍾", "🍷", "🍸", "🍹", "🍺", "🍻", "🥂", "🥃", "𫗗",
    "🥤", "🧋", "🧃", "🧉", "🧊", "🥢", "🍴", "🥄", "🔪", "💎", "💍", "👑", "🎩", "🎓", "⛑️", "💡", "💰", "💵", "💴",
    "💶", "💷", "💳", "🔑", "🚪", "🛋️", "🚽", "🚿", "🛁", "🔨", "⛏️", "⚙️", "🔧", "🔩", "🧱", "⛓️", "💣", "🔫", "🔪",
    "🛡️", "🚬", "⚰️", "🔮", "🧿", "📿", "💈", "⚗️", "🔭", "🔬", "💊", "💉", "🩸", "🩹", "🩺", "🌡️", "⚖️", "📜", "✉️",
    "📦", "📮", "🗳️", "🗓️", "📆", "📅", "📈", "📉", "📊", "📋", "📌", "📍", "📎", "📏", "📐", "✂️", "🗑️", "🔒", "🔓",
    "🔏", "🔐", "🔎", "📚", "📖", "🔖", "🏷️", "📰", "🗞️", "🎨", "🎬", "🎤", "🎧", "🎷", "🎸", "🎹", "🎺", "🎻", "🪕",
    "🥁", "📱", "💻", "🖥️", "🖱️", "💾", "💿", "📀", "🎥", "🎞️", "📽️", "📺", "📷", "📸", "📹", "📼", "🔍", "🔎", "🕯️",
    "💡", "🔦", "🏮", "🪔", "📔", "📕", "📗", "📘", "📙", "📓", "📒", "📝", "✏️", "✒️", "🖋️", "🖊️", "🖌️", "🖍️", "🖊️",
    "🖋️", "❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💔", "❣️", "💕", "💞", "💓", "💗", "💖", "💘", "💝",
    "💟", "☮️", "✝️", "☪️", "🕉️", "☸️", "✡️", "🔯", "🕎", "☯️", "☦️", "🛐", "⛎", "♈", "♉", "♊", "♋", "♌", "♍", "♎",
    "♏", "♐", "♑", "♒", "♓", "🆔", "⚛️", "🉑", "☢️", "☣️", "📴", "📳", "🈶", "🈚", "🈸", "🈺", "🈷️", "✴️", "🆚", "💮",
    "🉐", "㊙️", "㊗️", "🈴", "🈵", "🈹", "🈲", "🅰️", "🅱️", "🆎", "🆑", "🅾️", "🆘", "❌", "⭕", "🛑", "⛔", "📛", "🚫", "💯",
    "💢", "♨️", "🚷", "🚯", "🚳", "🚱", "🔞", "📵", "🚭", "❗", "❕", "❓", "❔", "‼️", "⁉️", "🔅", "🔆", "〽️", "⚠️",
    "🚸", "🔱", "⚜️", "🔰", "♻️", "✅", "🈯", "💹", "❇️", "✳️", "❎", "🌐", "💠", "Ⓜ️", "🌀", "💤", "🏧", "🚾", "♿", "🅿️",
    "🛗", "🈳", "🈂️", "🛂", "🛃", "🛄", "🛅", "🚹", "🚺", "🚼", "🚻", "🚮", "🎦", "📶", "🈁", "🔣", "ℹ️", "🔤", "🔡",
    "🔠", "🆖", "🆗", "🆙", "🆒", "🆕", "🆓", "0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟", "🔢",
    "#️⃣", "*️⃣", "⏏️", "▶️", "⏸️", "⏯️", "⏹️", "⏺️", "⏭️", "⏮️", "⏩", "⏪", "⏫", "⏬", "◀️", "🔼", "🔽", "➡️", "⬅️",
    "⬆️", "⬇️", "↗️", "↘️", "↙️", "↖️", "↕️", "↔️", "↪️", "↩️", "⤴️", "⤵️", "🔀", "🔁", "🔂", "🔄", "🔃", "🎵", "🎶",
    "➕", "➖", "➗", "✖️", "♾️", "💲", "💱", "™️", "©️", "®️", "🔚", "🔙", "🔛", "🔝", "🔜", "☑️", "🔘", "🔴", "🟠", "🟡",
    "🟢", "🔵", "🟣", "🟤", "⚫", "⚪", "🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "🟫", "⬛", "⬜", "◼️", "◻️", "◾", "◽", "▪️",
    "▫️", "🔶", "🔷", "🔸", "🔹", "🔺", "🔻", "💠", "🔘", "🔳", "🔲"
]

def get_or_create_daily_prompt():
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
        except Exception:
            db.session.rollback()
            daily_emojis_obj = DailyEmoji.query.filter_by(date_posted=today).first()
    return daily_emojis_obj

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    daily_emojis_obj = get_or_create_daily_prompt()
    emojis = daily_emojis_obj.emojis.split()
    return render_template('base.html', emojis=emojis)

@main.route('/dashboard')
@login_required
def dashboard():
    daily_emojis_obj = get_or_create_daily_prompt()
    user_story_for_today = Story.query.filter_by(
        author=current_user,
        daily_emoji_id=daily_emojis_obj.id
    ).first()
    return render_template('dashboard.html',
                           emojis=daily_emojis_obj.emojis,
                           user_story=user_story_for_today)

@main.route('/submit', methods=['POST'])
@login_required
def submit_story():
    story_content = request.form.get('story_content')
    daily_emojis_obj = get_or_create_daily_prompt()

    if moderation_enabled and gemini_model and story_content:
        try:
            emojis_for_prompt = daily_emojis_obj.emojis if daily_emojis_obj else ''
            prompt = f"""
            Analyze the user's story for relevance to the given emojis and for any harmful content.
            The story should be creatively related to the emojis, but be lenient to encourage imagination.
            Reject only if there is absolutely no possible connection or if it contains explicit content, hate speech, or severe toxicity.
            Respond with ONLY one of the following decisions: "Yes", "No, explicit", or "No, off-topic".
            EMOJIS: {emojis_for_prompt}
            USER STORY: \"{story_content}\"
            """
            response = gemini_model.generate_content(prompt)
            decision = response.text.strip()
            if "No" in decision:
                flash(f"Your story was flagged as inappropriate or off-topic. Please revise.", "danger")
                return redirect(url_for('main.dashboard'))
        except Exception as e:
            print(f"ERROR: Gemini API call failed: {e}")
            flash("Could not verify story content. Please try again later.", "warning")
            return redirect(url_for('main.dashboard'))

    if Story.query.filter_by(author=current_user, daily_emoji_id=daily_emojis_obj.id).first():
        return redirect(url_for('main.stories'))

    if not story_content or len(story_content) < 10:
        flash("Your story must be at least 10 characters long.", "warning")
        return redirect(url_for('main.dashboard'))

    try:
        new_story = Story(content=story_content, author=current_user, daily_emoji_id=daily_emojis_obj.id)
        current_user.update_streak(date.today())
        db.session.add(new_story)
        db.session.commit()
        flash(f"Story submitted! Your current streak: {current_user.current_streak} days!", "success")
        return redirect(url_for('main.stories'))
    except Exception as e:
        db.session.rollback()
        print(f"Error committing new story: {e}")
        flash("Error submitting your story. Please try again.", "error")
        return redirect(url_for('main.dashboard'))

@main.route('/stories')
@login_required
def stories():
    daily_emojis_obj = get_or_create_daily_prompt()
    if not Story.query.filter_by(author=current_user, daily_emoji_id=daily_emojis_obj.id).first():
        flash("You must post your own story before you can view others'.", "warning")
        return redirect(url_for('main.dashboard'))
    
    all_stories = Story.query.filter_by(daily_emoji_id=daily_emojis_obj.id).order_by(Story.timestamp.desc()).all()
    liked_stories = session.get('liked_stories', [])
    
    return render_template('stories.html',
                           stories=all_stories,
                           prompt_emojis=daily_emojis_obj.emojis,
                           liked_stories=liked_stories)

@main.route('/story/<int:story_id>')
@login_required
def story_detail(story_id):
    story = Story.query.get_or_404(story_id)
    comments = Comments.query.filter_by(story_id=story.id).order_by(Comments.timestamp.asc()).all()
    liked_stories = session.get('liked_stories', [])
    liked_comments = session.get('liked_comments', [])
    return render_template('story_detail.html',
                           story=story,
                           comments=comments,
                           liked_stories=liked_stories,
                           liked_comments=liked_comments)

@main.route('/story/<int:story_id>/comment', methods=['POST'])
@login_required
def add_comment(story_id):
    content = request.form.get('content')
    if not content or len(content.strip()) < 1:
        return jsonify({'success': False, 'message': 'Comment cannot be empty.'}), 400
    
    new_comment = Comments(content=content, story_id=story_id, user_id=current_user.id)
    db.session.add(new_comment)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'comment': {
            'id': new_comment.id,
            'content': new_comment.content,
            'username': current_user.username,
            'timestamp': new_comment.timestamp.strftime('%Y-%m-%d %H:%M'),
            'likes': 0,
            'user_id': current_user.id
        }
    })

@main.route('/comment/<int:comment_id>/like', methods=['POST'])
@login_required
def like_comment(comment_id):
    comment = Comments.query.get_or_404(comment_id)
    liked_list = session.get('liked_comments', [])
    if comment_id in liked_list:
        comment.likes = max(0, comment.likes - 1)
        liked_list.remove(comment_id)
        liked = False
    else:
        comment.likes += 1
        liked_list.append(comment_id)
        liked = True
    session['liked_comments'] = liked_list
    db.session.commit()
    return jsonify({'likes': comment.likes, 'liked': liked})

@main.route('/comment/<int:comment_id>/edit', methods=['POST'])
@login_required
def edit_comment(comment_id):
    comment = Comments.query.get_or_404(comment_id)
    if comment.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Not authorized.'}), 403
    new_content = request.json.get('content', '').strip()
    if not new_content:
        return jsonify({'success': False, 'message': 'Comment cannot be empty.'}), 400
    comment.content = new_content
    db.session.commit()
    return jsonify({'success': True, 'content': comment.content})

@main.route('/stories/<int:story_id>/like', methods=['POST'])
@login_required
def like_story(story_id):
    story = Story.query.get_or_404(story_id)
    liked_list = session.get('liked_stories', [])
    if story_id in liked_list:
        story.likes = max(0, story.likes - 1)
        liked_list.remove(story_id)
        liked = False
    else:
        story.likes += 1
        liked_list.append(story_id)
        liked = True
    session['liked_stories'] = liked_list
    db.session.commit()
    return jsonify({'likes': story.likes, 'liked': liked})

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        file = request.files.get('profile_pic')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            unique_filename = f"user_{current_user.id}_{filename}"
            upload_path = os.path.join('app', 'static', 'profile_pics')
            os.makedirs(upload_path, exist_ok=True)
            file.save(os.path.join(upload_path, unique_filename))
            current_user.profile_pic = f'profile_pics/{unique_filename}'
            db.session.commit()
            flash('Your profile picture has been updated!', 'success')
        return redirect(url_for('main.profile'))

    user_posts = Story.query.filter_by(author=current_user).order_by(Story.timestamp.desc()).all()
    user_comments = db.session.query(Comments, Story.content.label('story_content')).join(Story, Comments.story_id == Story.id).filter(Comments.user_id == current_user.id).order_by(Comments.timestamp.desc()).all()
    
    liked_ids = session.get('liked_stories', [])
    user_likes = Story.query.filter(Story.id.in_(liked_ids)).all() if liked_ids else []

    return render_template('user.html',
                           user_posts=user_posts,
                           user_comments=user_comments,
                           user_likes=user_likes)

@main.route('/streak')
@login_required
def streak():
    return render_template('streak.html', current_streak=current_user.current_streak)

@main.route('/home')
def home():
    return redirect(url_for('main.index'))

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/stories/<int:story_id>/edit', methods=['POST'])
@login_required
def edit_story(story_id):
    story = Story.query.get_or_404(story_id)
    if story.user_id != current_user.id:
        flash("You are not authorized to edit this story.", "danger")
        return jsonify({'success': False, 'message': 'Not authorized.'}), 403

    new_content = request.json.get('content', '').strip()
    if not new_content or len(new_content) < 10:
        return jsonify({'success': False, 'message': 'Story must be at least 10 characters long.'}), 400

    story.content = new_content
    db.session.commit()
    flash("Your story has been updated.", "success")
    return jsonify({'success': True, 'content': story.content})