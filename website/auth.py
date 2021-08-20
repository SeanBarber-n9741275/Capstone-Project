from flask import ( 
    Blueprint, flash, render_template, request, url_for, redirect
) 
from werkzeug.security import generate_password_hash,check_password_hash
from .models import User
from .forms import LoginForm,RegisterForm
from flask_login import login_user,login_required,logout_user, current_user, AnonymousUserMixin
from . import db
from functools import wraps


bp = Blueprint('auth', __name__ )

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role == "admin":
            return f(*args, **kwargs)
        else:
            flash("You need to be an admin to view this page.", 'danger')
            return redirect('/')
    return wrap

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.is_authenticated:
            return f(*args, **kwargs)
        else:
            flash("You must be logged in to view this page.", 'danger')
            return redirect('/')
    return wrap

def login_required_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.is_authenticated:
            return f(*args, **kwargs)
        else:
            flash("You need to be an admin to view this page.", 'danger')
            return redirect('/')
    return wrap

def login_required_tickets(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.is_authenticated:
            return f(*args, **kwargs)
        else:
            flash("You must be logged in to purchase tickets.", 'danger')
            return redirect(request.url)
    return wrap



class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.role = 'customer'

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
            error='Incorrect user name'
        #check the password - notice password hash function
        elif not check_password_hash(u1.password_hash, password): # takes the hash and password
            error='Incorrect password'
        if error is None:
            #all good, set the login_user of flask_login to manage the user
            login_user(u1)
            return redirect(url_for('main.index'))
        else:
            flash(error)

    return render_template('user.html', form=login_form,  heading='Login')

@bp.route('/register', methods=['GET','POST'])
def register():
    register = RegisterForm()
    #the validation of form submis is fine
    if (register.validate_on_submit() == True):
            #get username, password, contact number, address and email from the form
            uname =register.username.data
            pwd = register.password.data
            email=register.email.data
            contact_number = register.contactnumber.data
            address = register.address.data
            role=register.role.data
            #check if a user exists
            u1 = User.query.filter_by(name=uname).first()
            if u1:
                flash('User name already exists, please login')
                return redirect(url_for('auth.login'))
            # don't store the password - create password hash
            pwd_hash = generate_password_hash(pwd)
            #create a new user model object
            new_user = User(name=uname, password_hash=pwd_hash, emailid=email, contact_number = contact_number, address= address)
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
def logout():
    logout_user()
    return redirect('/')
