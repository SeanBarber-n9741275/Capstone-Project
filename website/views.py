from flask import Blueprint, render_template, request, session, url_for, flash, redirect
from flask_login.utils import login_required
from .models import User, Resume, ResumeLog

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
  resume = Resume.query.filter_by(user_id=user_id)
  resumelog = ResumeLog.query.filter_by(user_id=user_id)
  if user is None:
    flash(f'You must be logged in to see your profile', 'danger')
    return redirect('/')
  else:

    return render_template('profile.html', user=user, resume=resume, resumelog=resumelog)

@mainbp.route('/resume/<user_id>/<resume_id>', methods=['GET'])
@login_required
def resume (user_id,resume_id):
  user = User.query.filter_by(user_id=user_id).first_or_404()
  resume = Resume.query.filter_by(resume_id=resume_id).first_or_404()
  resumelog = ResumeLog.query.filter_by(user_id=user_id)
  if user is None:
    flash(f'You must be logged in to see your resumes', 'danger')
    return redirect('/')
  else:

    return render_template('resume.html', user=user, resume=resume, resumelog=resumelog)