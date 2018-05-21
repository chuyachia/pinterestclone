from flaskapp import db
from datetime import datetime


like = db.Table('like',
    db.Column('authorid', db.String, db.ForeignKey('user.userid')),
    db.Column('imageid', db.Integer, db.ForeignKey('image.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String, nullable=False, unique=True)
    username = db.Column(db.String, index=True, nullable=False)
    images = db.relationship('Image', backref='author', lazy='dynamic')
    likes = db.relationship('Image', secondary=like, backref='liker', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)
        
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    authorid = db.Column(db.String, db.ForeignKey('user.userid'),nullable=False)
    created = db.Column(db.DateTime,index=True,default=datetime.utcnow,nullable=False, )
    description = db.Column(db.String,nullable=False)
    url = db.Column(db.String,nullable=False)

    def __repr__(self):
        return '<Image {}>'.format(self.description)
    
        