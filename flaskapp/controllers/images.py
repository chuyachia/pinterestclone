from flask import render_template, session, redirect, url_for, request, flash, Blueprint
from .auth import login_required
from .db import get_db
from urllib.request import urlopen, Request

bp = Blueprint('images',__name__)

@bp.route('/')
def home():
    db_inst = get_db()
    imgs = db_inst.execute('''SELECT user_name,author_id,
    images.id AS id, created, description, url, likes 
    FROM images JOIN users ON images.author_id == users.user_id
    LIMIT 6''').fetchall()
    nentries = db_inst.execute("SELECT COUNT(*) AS nentries FROM images").fetchone()
    likes = []
    if 'twitter_oauth_token' in session:
        likes= db_inst.execute('SELECT image_id FROM likes WHERE author_id =?',
        (session['twitter_oauth_token']['user_id'],)).fetchall()
        likes = list(map(lambda x: x['image_id'], likes))
    return render_template('index.html',path="/",imgs=imgs,likes=likes,nentries=nentries[0],
    user=int(session['twitter_oauth_token']['user_id']) if 'twitter_oauth_token' in session else None)

@bp.route('/contimg/<n>')
def contimg(n):
    db_inst = get_db()
    imgs = db_inst.execute('''SELECT user_name,author_id,
    images.id AS id, created, description, url, likes 
    FROM images JOIN users ON images.author_id == users.user_id
    LIMIT 6 OFFSET ?''',(n,)).fetchall()
    likes = []
    if 'twitter_oauth_token' in session:
        likes= db_inst.execute('SELECT image_id FROM likes WHERE author_id =?',
        (session['twitter_oauth_token']['user_id'],)).fetchall()
        likes = list(map(lambda x: x['image_id'], likes))
    return render_template('images.html',imgs=imgs,likes=likes,
    user=int(session['twitter_oauth_token']['user_id']) if 'twitter_oauth_token' in session else None)
    
@bp.route('/<userid>')
def user_imgs(userid):
    db_inst = get_db()
    imgs = db_inst.execute('''SELECT user_name,author_id, images.id AS id, created, description, url, likes 
    FROM images JOIN users ON images.author_id == users.user_id 
    WHERE users.user_id == ?
    LIMIT 6''',(userid,)).fetchall()
    likes = []
    path = None
    if 'twitter_oauth_token' in session:
        likes= db_inst.execute('SELECT image_id FROM likes WHERE author_id =?',
        (session['twitter_oauth_token']['user_id'],)).fetchall()
        likes = list(map(lambda x: x['image_id'], likes))
        if session['twitter_oauth_token']['user_id'] == userid:
            path="/myimgs"
    return render_template('index.html',path=path,imgs=imgs,likes=likes,
    user=int(session['twitter_oauth_token']['user_id']) if 'twitter_oauth_token' in session else None)
    
@bp.route('/mylikes')
@login_required
def mylikes():
    db_inst = get_db()
    imgs = db_inst.execute('''SELECT user_name, images.author_id, images.id AS id, created, description, url, likes 
    FROM images JOIN likes ON images.id == likes.image_id JOIN users ON images.author_id == users.user_id 
    WHERE likes.author_id == ?''',(session['twitter_oauth_token']['user_id'],))
    likes = []
    if 'twitter_oauth_token' in session:
        likes= db_inst.execute('SELECT image_id FROM likes WHERE author_id =?',
        (session['twitter_oauth_token']['user_id'],)).fetchall()
        likes = list(map(lambda x: x['image_id'], likes))
    return render_template('index.html',path="/mylikes",imgs=imgs,likes=likes,
    user=int(session['twitter_oauth_token']['user_id']) if 'twitter_oauth_token' in session else None)
    
@bp.route('/new',methods=['POST'])
@login_required
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
            author_id = session['twitter_oauth_token']['user_id']
            desc = request.form['desc'] 
            db_inst = get_db()
            db_inst.execute("INSERT INTO images (author_id,url,description,likes) VALUES (?,?,?,?)",
            (author_id,url,desc,0))
            db_inst.commit()
    return redirect(url_for('images.home'))
     
@bp.route('/like',methods=['PUT'])
@login_required
def like():
    if request.method == 'PUT':
        db_inst = get_db()
        db_inst.execute("UPDATE images SET likes = likes + 1 WHERE id =? ",
        (request.form['id'],))
        db_inst.execute("INSERT INTO likes (author_id,image_id) VALUES (?,?)",
        (session['twitter_oauth_token']['user_id'],request.form['id']))
        db_inst.commit()
    return 'success'
    
    
@bp.route('/unlike',methods=['PUT'])
@login_required
def unlike():
    if request.method == 'PUT':
        db_inst = get_db()
        db_inst.execute("UPDATE images SET likes = likes -1 WHERE id =? ",
        (request.form['id'],))
        db_inst.execute("DELETE FROM likes WHERE author_id= ? AND image_id=?",
        (session['twitter_oauth_token']['user_id'],request.form['id']))
        db_inst.commit()
    return 'success'
    
@bp.route('/delete',methods=['DELETE'])
@login_required
def delete():
    if request.method == 'DELETE':
        db_inst = get_db()
        db_inst.execute("DELETE FROM images WHERE id=?",
        (request.form['id'],))
        db_inst.commit()
    return 'success'
    

    