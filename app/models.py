from datetime import datetime
import json

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    # TODO: see how this query looks, and if it needs performance tuning
    tweets = db.relationship('Tweet', backref='author', lazy='dynamic')
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


    def __repr__(self):
        return f'<User {self.username}>'


class Tweet(db.Model):
    __tablename__ = 'tweet'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.Text)
    dateadded = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # TODO: see how this query looks, and if it needs performance tuning
    replies = db.relationship('Reply', backref='reply', lazy='dynamic')


class Reply(db.Model):
    __tablename__ = 'reply'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    dateadded = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    tweet = db.Column(db.Integer, db.ForeignKey('tweet.id'))
    parent_reply = db.Column(db.Integer, db.ForeignKey('reply.id'), nullable=True)
