from flask import Flask,render_template, g, session, redirect, url_for, request, flash
import os
from .controllers import db
from .controllers.auth import login_required
from urllib.request import urlopen, Request

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskapp.sqlite'),
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    
    db.init_app(app)
    
    @app.route('/')
    def home():
        print(session)
        db_inst = db.get_db()
        imgs = db_inst.execute("SELECT * FROM images").fetchall()
        return render_template('index.html',path="/",imgs=imgs,
        user=session['twitter_oauth_token']['screen_name'] if 'twitter_oauth_token' in session else None)
        
        
    @app.route('/myimgs')
    def myimgs():
        return render_template('myimgs.html',path="/myimgs",
        user=session['twitter_oauth_token']['screen_name'] if 'twitter_oauth_token' in session else None)
    
    @app.route('/logout')
    def logout():
        if 'twitter_oauth_token' in session:
            session.pop('twitter_oauth_token')
        return redirect(url_for('home'))
        
    @login_required
    @app.route('/new',methods=['POST'])
    def addimg():
        if request.method == 'POST':
            url = request.form['url']
            error = None
            try:
                headers={
                    "Range": "bytes=0-10",
                    "User-Agent": "MyTestAgent",
                    "Accept":"*/*"
                }
                req = Request(url, headers=headers)
                res = urlopen(req)
                if not 'image' in res.info()['Content-Type']:
                    error="Not a valid image"
            except:
                error="Url does not exist"

            if error is not None:
                flash(error)
            else:
                user_name = session['twitter_oauth_token']['screen_name']
                user_id = session['twitter_oauth_token']['user_id']
                desc = request.form['desc'] 
                db_inst = db.get_db()
                db_inst.execute("INSERT INTO images (author_id,author_name,url,description) VALUES (?,?,?,?)",
                (user_id,user_name,url,desc))
                db_inst.commit()
        return redirect(url_for('home'))
            
    
    from .controllers.auth import blueprint
    app.register_blueprint(blueprint)
    

    return app