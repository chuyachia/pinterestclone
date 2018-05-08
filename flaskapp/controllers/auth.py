from flask import redirect, url_for, g, session
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
import functools

blueprint = make_twitter_blueprint(
    api_key="XHzlfq7iHkHinQ1MYROfDrzB2",
    api_secret="lCJW5rkAwHbmzdksLnyGM64lJv9EGvLhOOXLsA53pMbxgUoOOY",
)

@blueprint.route("/")
def index():
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))
    resp = twitter.get("account/settings.json")
    if 'ok' in resp:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))
    #g.user = resp.json()["screen_name"]
    
    
def login_required(view):
    """View decorator that redirects anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'twitter_oauth_token' in session:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view