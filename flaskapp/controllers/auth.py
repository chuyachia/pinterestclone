from flask import redirect, url_for, g, session, current_app 
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from .db import get_db
import functools
from ..config.config import Config



bp = make_twitter_blueprint(
    api_key=Config().twitterKey,
    api_secret=Config().twitterSecret,
    redirect_to='twitter.adduser'
)

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not 'twitter_oauth_token' in session:
            return redirect(url_for('twitter.login'))
        return view(**kwargs)
    return wrapped_view

@bp.route("/")
def index():
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))
    resp = twitter.get("account/settings.json")
    assert resp.ok
    return redirect(url_for('images.home'))

@bp.route('/logout')
def logout():
    if 'twitter_oauth_token' in session:
        session.pop('twitter_oauth_token')
    return redirect(url_for('images.home'))

@bp.route("/adduser")
@login_required
def adduser():
    db_inst = get_db()
    user = db_inst.execute('SELECT * FROM users WHERE user_id == (?)',(session['twitter_oauth_token']['user_id'],)).fetchone()
    if user is None:
        print('Add new user')
        db_inst.execute('INSERT INTO users (user_id,user_name) VALUES (?,?)',(session['twitter_oauth_token']['user_id'],
        session['twitter_oauth_token']['screen_name']))
        db_inst.commit()
    elif not user['user_name'] == session['twitter_oauth_token']['screen_name']:
        print('Update username to existing user')
        db_inst.execute('UPDATE users SET user_name=?',(session['twitter_oauth_token']['screen_name'],))
        db_inst.commit()
    return redirect(url_for('images.home'))
    
