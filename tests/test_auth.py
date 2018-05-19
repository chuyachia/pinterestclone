import pytest
from flask import session, url_for
   
def test_generate_login_url(app):
    with app.test_request_context("/"):
        login_url = url_for("twitter.login")
        assert login_url == "/auth/twitter"

def test_logout(auth,client):
    with client:
        auth.login()
        client.get('/')
        assert session['twitter_oauth_token'] == {'user_id':'1',"screen_name":'test1'} 
        auth.logout()
        assert 'twitter_oauth_token' not in session
        
def test_add_user(auth,client):
    with client:
        auth.login()
        res = client.get('/auth/adduser')
        assert res.status_code==302
        assert res.headers['location'] == 'http://localhost/' # redirect to home when logged in
        auth.logout()
        res = client.get('/auth/adduser')
        assert res.status_code==302
        assert res.headers['location'] == 'http://localhost/auth/twitter'  # redirect to login page when not loggedin
        
        
        
        
        
    