from flask import Blueprint, render_template, request, session, url_for, flash, redirect
from flask_login.utils import login_required
from .models import User
#from website.models import Event

mainbp = Blueprint('main', __name__)


@mainbp.route('/')
def index():
    return render_template('index.html')

@mainbp.route('/home')
def home():
    return render_template('index.html')

@mainbp.route('/about')
def about():
    return render_template('about.html')

@mainbp.route('/tips')
def tips():    
    return render_template('tips.html')

@mainbp.route('/upload')
def upload():
    return render_template('upload.html')

@mainbp.route('/profile/<user_id>', methods=['GET'])
@login_required
def profile (user_id):
  user = User.query.filter_by(user_id=user_id).first_or_404()
  if user is None:
    flash(f'You must be logged in to see your profile')
    return redirect('/')
  else:

    return render_template('profile.html', user=user)