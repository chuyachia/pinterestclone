import os
import tempfile
import pytest
from flaskapp import create_app
from flaskapp import db
from flaskapp.models import User, Image

basedir = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def app():
    app = create_app({
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' +os.path.join(basedir, 'test.db'),
        'TESTING': True,
        'WTF_CSRF_ENABLED':False
    })
    
    with app.app_context():
        db.create_all()
        db.session.commit()
    yield app
    


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self):
        with self._client.session_transaction() as sess:
            sess['twitter_oauth_token']={}
            sess['twitter_oauth_token']['user_id'] = "1"
            sess['twitter_oauth_token']['screen_name'] = "test1"
    
    def logout(self):
        return self._client.get('/auth/logout')

@pytest.fixture
def auth(client):
    return AuthActions(client)