from flask import render_template, session, redirect, url_for, request, flash, Blueprint
from flaskapp.auth import login_required
from urllib.request import urlopen, Request
from .components.forms import AddNewForm
from flaskapp import db
from flaskapp.models import User, Image

bp = Blueprint('images',__name__)

@bp.route('/')
def home():
    imgs = Image.query.join(User).add_columns(User.username).limit(6).all()
    imgs = list(map(lambda x:{'username':x[1],'authorid':x[0].authorid, 'id':x[0].id,
        'created':x[0].created.strftime("%Y-%m-%d"),'description':x[0].description,
        'url':x[0].url,'likes':len(x[0].liker)
    },imgs))
    nentries = Image.query.count()
    likes = []
    if 'twitter_oauth_token' in session:
        likes = Image.query.filter(Image.liker.any(userid=session['twitter_oauth_token']['user_id'])).all()
        likes = list(map(lambda x: x.id,likes))
    return render_template('index.html',path="/",imgs=imgs,likes=likes,nentries=nentries,form = AddNewForm(request.form),
    title="Home", user=session['twitter_oauth_token']['user_id'] if 'twitter_oauth_token' in session else None)

@bp.route('/contimg/<n>')
def contimg(n):
    imgs = Image.query.join(User).add_columns(User.username).offset(n).limit(6).all()
    imgs = list(map(lambda x:{'username':x[1],'authorid':x[0].authorid, 'id':x[0].id,
        'created':x[0].created.strftime("%Y-%m-%d"),'description':x[0].description,
        'url':x[0].url,'likes':len(x[0].liker)
    },imgs))
    likes = []
    if 'twitter_oauth_token' in session:
        likes = Image.query.filter(Image.liker.any(userid=session['twitter_oauth_token']['user_id'])).all()
        likes = list(map(lambda x: x.id,likes))
    return render_template('images.html',imgs=imgs,likes=likes,
    user=session['twitter_oauth_token']['user_id'] if 'twitter_oauth_token' in session else None)
    
@bp.route('/<userid>')
def user_imgs(userid):
    user = User.query.filter_by(userid=userid).first()
    imgs= []
    likes = []
    path = None
    if not user :
       return render_template('index.html',path=path,imgs=imgs,likes=likes,form = AddNewForm(request.form),
       title="Not Found", user=int(session['twitter_oauth_token']['user_id']) if 'twitter_oauth_token' in session else None),404
    username = user.username
    imgs = Image.query.join(User).filter_by(userid=userid).add_columns(User.username).all()
    imgs = list(map(lambda x:{'username':x[1],'authorid':x[0].authorid, 'id':x[0].id,
        'created':x[0].created.strftime("%Y-%m-%d"),'description':x[0].description,
        'url':x[0].url,'likes':len(x[0].liker)
    },imgs))
    if 'twitter_oauth_token' in session:
        likes = Image.query.filter(Image.liker.any(userid=session['twitter_oauth_token']['user_id'])).all()
        likes = list(map(lambda x: x.id,likes))
        if session['twitter_oauth_token']['user_id'] == userid:
            path="/myimgs"
    return render_template('index.html',path=path,imgs=imgs,likes=likes,form = AddNewForm(request.form),
    title=username+"'s Wall",user=session['twitter_oauth_token']['user_id'] if 'twitter_oauth_token' in session else None)
    
@bp.route('/mylikes')
@login_required
def mylikes():
    imgs = Image.query.join(User).add_columns(User.username).\
    filter(Image.liker.any(userid=session['twitter_oauth_token']['user_id'])).all()
    imgs = list(map(lambda x:{'username':x[1],'authorid':x[0].authorid, 'id':x[0].id,
        'created':x[0].created.strftime("%Y-%m-%d"),'description':x[0].description,
        'url':x[0].url,'likes':len(x[0].liker)
    },imgs))
    likes = []
    if 'twitter_oauth_token' in session:
        likes = Image.query.filter(Image.liker.any(userid=session['twitter_oauth_token']['user_id'])).all()
        likes = list(map(lambda x: x.id,likes))
    return render_template('index.html',path="/mylikes",imgs=imgs,likes=likes,form = AddNewForm(request.form),
    title="My Likes",user=session['twitter_oauth_token']['user_id'] if 'twitter_oauth_token' in session else None)
    
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
            author = User.query.filter_by(userid= session['twitter_oauth_token']['user_id']).first()
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
        img = Image.query.filter_by(id=request.form['id']).first()
        user = User.query.filter_by(userid=session['twitter_oauth_token']['user_id']).first()
        if img:
            img.liker.append(user)
            db.session.commit()
            return 'success',200
    return 'fail', 404
    
    
@bp.route('/unlike',methods=['PUT'])
@login_required
def unlike():
    if request.method == 'PUT':
        img = Image.query.filter_by(id=request.form['id']).first()
        user = User.query.filter_by(userid=session['twitter_oauth_token']['user_id']).first()
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
    

    