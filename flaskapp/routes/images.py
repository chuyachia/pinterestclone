from flask import render_template, session, redirect, url_for, request, flash, Blueprint
from flaskapp.routes.auth import login_required
from urllib.request import urlopen, Request
from flaskapp.components.forms import AddNewForm
from flaskapp import db
from flaskapp.models import User, Image
from flaskapp.controllers import get_next_n_imgs, get_user_likes, get_user, get_user_imgs, get_user_liked_imgs, get_img

bp = Blueprint('images',__name__)
nimgload = 3

@bp.route('/')
def home():
    nentries = Image.query.count()
    return render_template('index.html',
    path="/",imgs=[],likes=[],
    nentries=nentries,
    form = AddNewForm(request.form),
    title="Home", 
    user=session['twitter_oauth_token']['user_id'] if 'twitter_oauth_token' in session else None)

@bp.route('/page/<n>')
def contimg(n):
    n = int(n)
    imgs = get_next_n_imgs(n,nimgload)
    likes = []
    if 'twitter_oauth_token' in session:
        likes = get_user_likes(session['twitter_oauth_token']['user_id'])
    return render_template('images.html',
    imgs=imgs,likes=likes,
    nentries=None,
    form = AddNewForm(request.form),
    user=session['twitter_oauth_token']['user_id'] if 'twitter_oauth_token' in session else None)
    
@bp.route('/<userid>')
@bp.route('/myimgs')
def user_imgs(userid=None):
    userid = userid or session['twitter_oauth_token']['user_id']
    user = get_user(userid)
    imgs= []
    likes = []
    path = None
    if not user :
       return render_template('index.html',
       path=path,imgs=imgs,
       likes=likes,form = AddNewForm(request.form),
       title="Not Found", 
       user=int(session['twitter_oauth_token']['user_id']) if 'twitter_oauth_token' in session else None),404
    username = user.username
    imgs = get_user_imgs(userid)
    if 'twitter_oauth_token' in session:
        likes = get_user_likes(session['twitter_oauth_token']['user_id'])
        if session['twitter_oauth_token']['user_id'] == userid:
            path="/myimgs"
    return render_template('index.html',path=path,
    imgs=imgs,likes=likes,form = AddNewForm(request.form),nentries=0,
    title=username+"'s Wall",
    user=session['twitter_oauth_token']['user_id'] if 'twitter_oauth_token' in session else None)
    
@bp.route('/mylikes')
@login_required
def mylikes():
    imgs = get_user_liked_imgs(session['twitter_oauth_token']['user_id'])
    likes = []
    if 'twitter_oauth_token' in session:
        likes = get_user_likes(session['twitter_oauth_token']['user_id'])
    return render_template('index.html',path="/mylikes",
    imgs=imgs,likes=likes,form = AddNewForm(request.form),
    nentries=0,title="My Likes",
    user=session['twitter_oauth_token']['user_id'] if 'twitter_oauth_token' in session else None)
    
@bp.route('/new',methods=['POST'])
@login_required
def addimg():
    form = AddNewForm(request.form)
    if form.validate():
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
            author = get_user(session['twitter_oauth_token']['user_id'])
            desc = form.desc.data
            img = Image(description = desc, url = url ,author = author)
            db.session.add(img)
            db.session.commit()
            flash('New image added','success')
    return redirect(url_for('images.home'))
     
@bp.route('/like',methods=['PUT'])
@login_required
def like():
    if request.method == 'PUT':
        img = get_img(request.form['id'])
        user = get_user(session['twitter_oauth_token']['user_id'])
        if img:
            img.liker.append(user)
            db.session.commit()
            return 'success',200
    return 'fail', 404
    
    
@bp.route('/unlike',methods=['PUT'])
@login_required
def unlike():
    if request.method == 'PUT':
        img = get_img(request.form['id'])
        user = get_user(session['twitter_oauth_token']['user_id'])
        if img:
            img.liker.remove(user)
            db.session.commit()
            return 'success', 200
    return 'fail', 404
    
@bp.route('/delete',methods=['DELETE'])
@login_required
def delete():
    if request.method == 'DELETE':
        imgs = Image.query.filter(Image.author.has(userid = session['twitter_oauth_token']['user_id']),
        Image.id == request.form['img_id']).first()
        if imgs:
            db.session.delete(imgs)
            db.session.commit()
            return 'success',200
    return 'fail', 403
    

    