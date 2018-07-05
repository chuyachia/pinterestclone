from flaskapp.models import User, Image

def format_imgs_data(imgs):
    return list(map(lambda x:{
        'username':x[1],'authorid':x[0].authorid, 'id':x[0].id,
        'created':x[0].created.strftime("%Y-%m-%d"),'description':x[0].description,
        'url':x[0].url,'likes':len(x[0].liker)
    },imgs))
    
def get_img(imgid):
    return Image.query.filter_by(id=imgid).first()
def get_next_n_imgs(n_load,n_imgs):
    imgs = Image.query.join(User).add_columns(User.username).offset(n_load*n_imgs).limit(n_imgs).all()
    return format_imgs_data(imgs)
    
def get_user_likes(userid):
    likes = Image.query.filter(Image.liker.any(userid=userid)).all()
    return list(map(lambda x: x.id,likes))

def get_user(userid):
    return User.query.filter_by(userid=userid).first()
    
def get_user_imgs(userid):
    imgs = Image.query.join(User).filter_by(userid=userid).add_columns(User.username).all()
    return format_imgs_data(imgs)
    
def get_user_liked_imgs(userid):
    imgs = Image.query.join(User).add_columns(User.username).filter(Image.liker.any(userid=userid)).all()
    return format_imgs_data(imgs)
    