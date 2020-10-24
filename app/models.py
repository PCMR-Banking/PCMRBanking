from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5

class User(UserMixin, db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    accounts = db.relationship('Accounts', backref='owner', lazy='dynamic')
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    cellphone = db.Column(db.String(12))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, passw):
        self.password = generate_password_hash(passw)

    def check_password(self, passw):
        return check_password_hash(self.password, passw)

    def get_id(self):
           return (self.ID)

    def avatar(self, size):
        digest = md5(self.username.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

class Accounts(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    Created = db.Column(db.DateTime, default=datetime.utcnow)
    AccountType = db.Column(db.String(25), default='Standard Account')
    AccountBalance = db.Column(db.Integer, default=500)
    AccountName = db.Column(db.String(50), index=True, default='Standard Account')
    ownerID = db.Column(db.Integer, db.ForeignKey('user.ID'))

    def __repr__(self):
        return '<Accounts {}>'.format(self.AccountName)


@login.user_loader
def load_user(ID):
    return User.query.get(int(ID))