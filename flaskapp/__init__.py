from flask import Flask,render_template, g, session, redirect, url_for, request, flash
from flaskapp.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_object(Config)
    if test_config is not None:
        app.config.update(test_config)
    db.init_app(app)
    migrate.init_app(app,db)
    
    from . import auth, images
    app.register_blueprint(auth.bp, url_prefix="/auth")
    app.register_blueprint(images.bp)
    
    return app
from flaskapp import models