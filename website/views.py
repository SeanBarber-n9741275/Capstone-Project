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
from website.results import get_results
import pandas as pd
import json
import plotly
import plotly.express as px
sample_pdf = open('website/static/Sample_Resume2.pdf', 'rb')


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
            new_id = newResume.resume_id
            return redirect("/results/%s/%s" % (current_user.user_id, new_id))

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
  resume = Resume.query.filter_by(resume_id=resume_id).first_or_404()
  resumelog = ResumeLog.query.filter_by(resume_id=resume_id)

  return render_template('resume.html', user=user, resume=resume, resumelog=resumelog)


@mainbp.route('/results/<user_id>/<resume_id>', methods=['GET'])
@login_required
def results (user_id,resume_id):
  user = User.query.filter_by(user_id=current_user.user_id).first_or_404()
  resume = Resume.query.filter_by(resume_id=resume_id).first_or_404()
  resumelog = ResumeLog.query.filter_by(resume_id=resume_id)
  resumefile = open("website/" + resume.resumecontents, 'rb')
  results = get_results(resumefile)
  df = pd.DataFrame({
    "Keyword": results[0],
    "Score": results[1]
  })

  fig = px.bar(df, x="Score", y="Keyword", orientation="h")

  graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

  return render_template('results.html', graphJSON=graphJSON, results_labels=results[0], results_values=results[1], resume=resume)#user=user,, resumelog=resumelog, results=results)
