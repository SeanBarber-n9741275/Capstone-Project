from flask import ( 
    Blueprint, flash, render_template, request, url_for, redirect
) 
from werkzeug.security import generate_password_hash,check_password_hash
from .models import User
from .forms import LoginForm,RegisterForm
from flask_login import login_user,login_required,logout_user, current_user, AnonymousUserMixin
from . import db
from functools import wraps

#Defining the blueprint
bp = Blueprint('auth', __name__ )

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        #check if user is authenticated, if not redirect to home page and flash warning
        if current_user.is_authenticated:
            return f(*args, **kwargs)
        else:
            flash("You must be logged in to view this page.", 'danger')
            return redirect('/')
    return wrap


@bp.route('/login', methods=['GET','POST'])
def login():
    login_form = LoginForm()
    error=None
    if login_form.validate_on_submit():
        user_name = login_form.username.data
        password = login_form.password.data
        u1 = User.query.filter_by(name=user_name).first()
        #if there is no user with that name
        if u1 is None:
            error='Incorrect user name or password'
        #check the password - notice password hash function
        elif not check_password_hash(u1.password_hash, password): # takes the hash and password
            error='Incorrect user name or password'
        if error is None:
            #all good, set the login_user of flask_login to manage the user
            login_user(u1)
            return redirect(url_for('main.index'))
        else:
            flash(error, 'danger')

    return render_template('user.html', form=login_form,  heading='Login')

@bp.route('/register', methods=['GET','POST'])
def register():
    register = RegisterForm()
    #the validation of form submis is fine
    if (register.validate_on_submit() == True):
            #get username, password, contact number, address and email from the form
            uname =register.name.data
            pwd = register.password.data
            email=register.email.data
            area_of_expertise = register.area_of_expertise.data
            gender = register.gender.data
            birthdate = register.birthdate.data
            #check if a user exists
            u1 = User.query.filter_by(name=uname).first()
            if u1:
                flash('User name already exists, please login', 'danger')
                return redirect(url_for('auth.login'))
            # don't store the password - create password hash
            pwd_hash = generate_password_hash(pwd)
            #create a new user model object
            new_user = User(name=uname, password_hash=pwd_hash, email=email, area_of_expertise = area_of_expertise, gender= gender, birthdate = birthdate)
            db.session.add(new_user)
            db.session.commit()
            #commit to the database and redirect to HTML page
            flash("New account created!", 'success')
            return redirect(url_for('main.index'))
    #the else is called when there is a get message
    else:
        return render_template('user.html', form=register, heading='Register')


@bp.route('/logout')
@login_required
#Allows logged in user to log out and redirects to home page
def logout():
    logout_user()
    return redirect('/')
