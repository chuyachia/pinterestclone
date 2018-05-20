from flask import render_template, session, redirect, url_for, request, flash, Blueprint
from .auth import login_required
from .db import get_db
from urllib.request import urlopen, Request
from .components.forms import AddNewForm

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
    return render_template('index.html',path="/",imgs=imgs,likes=likes,nentries=nentries[0],form = AddNewForm(),
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
    likes = []
    path = None
    imgs = db_inst.execute('''SELECT user_name,author_id, images.id AS id, created, description, url, likes 
    FROM images JOIN users ON images.author_id == users.user_id 
    WHERE users.user_id == ?
    LIMIT 6''',(userid,)).fetchall()
    if len(imgs)  == 0:
           return render_template('index.html',path=path,imgs=imgs,likes=likes,
           user=int(session['twitter_oauth_token']['user_id']) if 'twitter_oauth_token' in session else None),404
    if 'twitter_oauth_token' in session:
        likes= db_inst.execute('SELECT image_id FROM likes WHERE author_id =?',
        (session['twitter_oauth_token']['user_id'],)).fetchall()
        likes = list(map(lambda x: x['image_id'], likes))
        if session['twitter_oauth_token']['user_id'] == userid:
            path="/myimgs"
    return render_template('index.html',path=path,imgs=imgs,likes=likes,form = AddNewForm(),
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
    return render_template('index.html',path="/mylikes",imgs=imgs,likes=likes,form = AddNewForm(),
    user=int(session['twitter_oauth_token']['user_id']) if 'twitter_oauth_token' in session else None)
    
@bp.route('/new',methods=['POST'])
@login_required
def addimg():
    form = AddNewForm()
    if form.validate_on_submit():
        url =form.url.data
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
            flash(error,'error')
        else:
            author_id = session['twitter_oauth_token']['user_id']
            desc = form.desc.data 
            db_inst = get_db()
            db_inst.execute("INSERT INTO images (author_id,url,description,likes) VALUES (?,?,?,?)",
            (author_id,url,desc,0))
            db_inst.commit()
            flash('New image added','success')
    return redirect(url_for('images.home'))
     
@bp.route('/like',methods=['PUT'])
@login_required
def like():
    if request.method == 'PUT':
        db_inst = get_db()
        img = db_inst.execute("SELECT * FROM images WHERE id =? ",
        (request.form['id'],)).fetchone()
        if img:
            db_inst.execute("UPDATE images SET likes = likes + 1 WHERE id =? ",
            (request.form['id'],))
            db_inst.execute("INSERT INTO likes (author_id,image_id) VALUES (?,?)",
            (session['twitter_oauth_token']['user_id'],request.form['id']))
            db_inst.commit()
            return 'success',200
    return 'fail', 404
    
    
@bp.route('/unlike',methods=['PUT'])
@login_required
def unlike():
    if request.method == 'PUT':
        db_inst = get_db()
        img = db_inst.execute("SELECT * FROM images WHERE id =? ",
        (request.form['id'],)).fetchone()
        if img:
            db_inst.execute("UPDATE images SET likes = likes -1 WHERE id =? ",
            (request.form['id'],))
            db_inst.execute("DELETE FROM likes WHERE author_id= ? AND image_id=?",
            (session['twitter_oauth_token']['user_id'],request.form['id']))
            db_inst.commit()
            return 'success', 200
    return 'fail', 404
    
@bp.route('/delete',methods=['DELETE'])
@login_required
def delete():
    if request.method == 'DELETE':
        db_inst = get_db()
        img_author= db_inst.execute("SELECT id, author_id FROM images WHERE id =?",(request.form['img_id'],)).fetchone()
        if str(img_author['author_id']) == session['twitter_oauth_token']['user_id']:
            db_inst.execute("DELETE FROM images WHERE id=?",
            (request.form['img_id'],))
            db_inst.execute("DELETE FROM likes WHERE image_id=?",
            (request.form['img_id'],))
            db_inst.commit()
            return 'success',200
    return 'fail', 403
    

    