import sqlite3

import pytest
from flaskapp.controllers.db import get_db


def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()

def test_user_table(app):
    with app.app_context():
        db= get_db()
        entries = db.execute('SELECT * FROM users').fetchall()
        assert len(entries) == 3
        
def test_images_table(app):
    with app.app_context():
        db= get_db()
        entries = db.execute('SELECT * FROM images').fetchall()
        assert len(entries) == 3

def test_likes_table(app):
    with app.app_context():
        db= get_db()
        entries = db.execute('SELECT * FROM likes').fetchall()
        assert len(entries) == 2