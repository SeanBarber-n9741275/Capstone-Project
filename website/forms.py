from flask_wtf import FlaskForm
from flask_wtf.recaptcha import validators
from werkzeug import datastructures
from wtforms.validators import DataRequired, InputRequired, Email, EqualTo
from wtforms.fields import *
from wtforms.fields.html5 import TimeField, DateTimeField, DateField
from wtforms.widgets.html5 import DateInput
from flask_wtf.file import FileRequired, FileField, FileAllowed
from werkzeug.utils import secure_filename
import os
from flask_sqlalchemy import SQLAlchemy

ALLOWED_FILES = {'png', 'jpg', 'PNG', 'JPG'}

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired('Please enter a username')])
    password = PasswordField('Password', validators=[InputRequired('Please enter a password')])

    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired('Please enter your full name')])
    email = StringField('Email', validators=[InputRequired('Please enter an email'), Email()])
    gender = StringField('Gender', validators=[InputRequired('Please enter your gender')])
    birthdate = DateField('Date of Birth', validators=[DataRequired('Please enter your date of birth')])
    area_of_expertise = StringField('Area of Expertise', validators=[InputRequired('Please enter your area of expertise')])
    password = PasswordField('Password', validators=[InputRequired('Please enter a password')])
    confirm = PasswordField('Password Confirmation', validators=[InputRequired(), EqualTo('password', 'Passwords do not match')])
    
    


    submit = SubmitField('Register')




