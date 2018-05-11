from flask import Flask,render_template, g, session, redirect, url_for, request, flash
import os

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskapp.sqlite'),
        SEND_FILE_MAX_AGE_DEFAULT = 0
    )
    #if test_config is None:
    #    app.config.from_pyfile('config.py', silent=True)
    #else:
    #    app.config.from_mapping(test_config)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from .controllers import db
    db.init_app(app)
    
    from .controllers import auth, images
    app.register_blueprint(auth.bp, url_prefix="/auth")
    app.register_blueprint(images.bp)
    
    return app