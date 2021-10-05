from flask import Blueprint, render_template, request, session, url_for, flash, redirect, current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from . import UPLOAD_FOLDER, allowed_file, db
from flask.ctx import AppContext
from flask_login import current_user
from flask_login.mixins import UserMixin
import os
from .auth import login_required
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

@mainbp.route('/upload', methods=['GET','POST'])
@login_required
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'resume' not in request.files:
            flash('No resume')
            return redirect(request.url)
        resume = request.files['resume']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if resume.filename == '':
            flash('No selected file')
            return render_template('upload.html')
        if resume and allowed_file(resume.filename):
            filename = secure_filename(resume.filename)
            resume.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            newResume = Resume(user_id=current_user.user_id, resumename=resume.filename, resumecontents=(os.path.join('static/resumes', filename)))
            db.session.add(newResume)
            db.session.commit()
            return render_template('upload.html')

    return render_template('upload.html')

@mainbp.route('/profile/<user_id>', methods=['GET'])
@login_required
def profile (user_id):
  user = User.query.filter_by(user_id=current_user.user_id).first_or_404()
  resume = Resume.query.filter_by(user_id=current_user.user_id)
  resumelog = ResumeLog.query.filter_by(user_id=current_user.user_id)

  return render_template('profile.html',user=user, resume=resume, resumelog=resumelog)

@mainbp.route('/resume/<user_id>/<resume_id>', methods=['GET'])
@login_required
def resume (user_id,resume_id):
  user = User.query.filter_by(user_id=current_user.user_id).first_or_404()
  resume = Resume.query.filter_by(user_id=current_user.user_id).first_or_404()
  resumelog = ResumeLog.query.filter_by(user_id=user.user_id)

  return render_template('resume.html', user=user, resume=resume, resumelog=resumelog)
  