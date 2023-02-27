from datetime import datetime
import json

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .utils.common import TokenGenerator


db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    dateadded = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    dateupdated = db.Column(db.DateTime, index=True, onupdate=datetime.utcnow)

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
    
    @classmethod
    def get_from_bearer_token(self, auth_token):
        auth_token = auth_token.replace('Bearer ', '')
        token = TokenGenerator.decode_token(auth_token)
        return User.query.filter_by(id=token.get('id')).first()

    def __repr__(self):
        return f'<User {self.username}>'


class Tweet(db.Model):
    __tablename__ = 'tweet'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.Text)
    dateadded = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    dateupdated = db.Column(db.DateTime, index=True, onupdate=datetime.utcnow)
    parent_id = db.Column(db.Integer, db.ForeignKey('tweet.id'), nullable=True)
    children = db.relationship("Tweet", backref=db.backref("parent", remote_side=[id]))
    likes = db.relationship("Like", backref=db.backref("like"))

    def to_json(self):
        return {
            'id': self.id,
            'body': self.body,
            'dateadded': self.dateadded,
            'dateupdated': self.dateupdated,
            'children': [child.id for child in self.children],
            'parent_id': self.parent_id,
            # TODO: is there a more efficient way to find this?
            'num_likes': len(self.likes)
        }


class Like(db.Model):
    __tablename__ = 'like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweet.id'), nullable=True)
    __table_args__ = (
        db.UniqueConstraint('user_id', 'tweet_id', name='uix_like__user_id__tweet_id'),
    )


class Retweet(db.Model):
    __tablename__ = 'retweet'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweet.id'))