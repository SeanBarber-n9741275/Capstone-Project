from datetime import datetime
from enum import unique
from . import db
from flask_login import UserMixin
from hashlib import md5



class User(db.Model,UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, nullable=True)
    email = db.Column(db.String(100), unique=True, index=True, nullable=True)
    gender = db.Column(db.String(100), index=True, nullable=True)
    birthdate = db.Column(db.Date, index=True, nullable=True)
    area_of_expertise = db.Column(db.String(100), index=True, nullable=True)
    password_hash = db.Column(db.String(10), nullable=False)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    
    
    # Flask-Login integration
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.user_id

class Resume(db.Model):
    __tablename__ = 'resumes'  
    resume_id = db.Column(db.Integer, primary_key=True)
    resumename = db.Column(db.String(100))
    area_of_expertise = db.Column(db.String(100))
    resumecontents = db.Column(db.String(400))

    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))



class ResumeLog(db.Model):
    __tablename__ = 'resumelog' 
    resumelog_id = db.Column(db.Integer, primary_key=True)
    result = db.Column(db.Integer)

    # foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.resume_id'))
