from datetime import datetime
from enum import unique
from . import db
from flask_login import UserMixin



class User(db.Model,UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, nullable=True)
    gender = db.Column(db.String(100), index=True, nullable=True)
    birthdate = db.Column(db.DateTime, index=True, nullable=True)
    emailid = db.Column(db.String(100), unique=True, index=True, nullable=True)
    password_hash = db.Column(db.String(10), nullable=False)
    
    
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
        return self.id
