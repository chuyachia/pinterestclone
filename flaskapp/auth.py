from flask import redirect, url_for, g, session 
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from flaskapp.models import User
from flaskapp import db
import os
import functools


bp = make_twitter_blueprint(
    api_key=os.environ.get('TWITTER_KEY'),
    api_secret=os.environ.get('TWITTER_SECRET'),
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
    user = User.query.filter_by(userid = session['twitter_oauth_token']['user_id']).first()
    if user is None:
        print('Add new user')
        newuser = User(userid = session['twitter_oauth_token']['user_id'], username = session['twitter_oauth_token']['screen_name'])
        db.session.add(newuser)
        db.session.commit()
    elif not user.username == session['twitter_oauth_token']['screen_name']:
        print('Update username to existing user')
        user.username = session['twitter_oauth_token']['screen_name']
        db.session.commit()
    return redirect(url_for('images.home'))
    
