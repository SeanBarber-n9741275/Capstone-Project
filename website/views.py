from flask import Blueprint, render_template, request, session, url_for, flash, redirect, current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from . import UPLOAD_FOLDER, allowed_file, db
from flask.ctx import AppContext
from flask_login import current_user
from flask_login.mixins import UserMixin
import os
import pathlib
from .auth import login_required
from .models import User, Resume, ResumeLog
from website.results import get_results
import pandas as pd
import json
import plotly
import plotly.express as px

mainbp = Blueprint('main', __name__)

#setting up the pages using Flask
@mainbp.route('/')
def index():
    #renders the index.html template when the website is at the main page
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
        expertise = request.form.get('expertise')
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
        #if the resume has a name is the allowed filetype, save the resume to the relevant folder and add it to the database
        if resume and allowed_file(resume.filename):
            filename = secure_filename(resume.filename)
            pathlib.Path("website/%s" % current_app.config['UPLOAD_FOLDER'], str(current_user.user_id)).mkdir(exist_ok=True)
            resume.save(os.path.join("website/%s" % current_app.config['UPLOAD_FOLDER'],str(current_user.user_id), filename))
            newResume = Resume(user_id=current_user.user_id, resumename=resume.filename, area_of_expertise=expertise, resumecontents=(os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user.user_id), filename)))
            db.session.add(newResume)
            db.session.commit()
            new_id = newResume.resume_id
            #redirecting to the results
            return redirect("/results/%s/%s" % (current_user.user_id, new_id))

    return render_template('upload.html')

@mainbp.route('/profile/<user_id>', methods=['GET'])
@login_required
def profile (user_id):
#using the current user's information to create their profile page
  user = User.query.filter_by(user_id=current_user.user_id).first_or_404()
  resume = Resume.query.filter_by(user_id=current_user.user_id)
  resumelog = ResumeLog.query.filter_by(user_id=current_user.user_id)
  #resumelog = resumelog.order_by(Resume.resume_id)

  return render_template('profile.html',user=user, resume=resume, resumelog=resumelog)

@mainbp.route('/resume/<user_id>/<resume_id>', methods=['GET'])
@login_required
def resume (user_id,resume_id):
#using the current user's resume information to create each resume page
  user = User.query.filter_by(user_id=current_user.user_id).first_or_404()
  resume = Resume.query.filter_by(resume_id=resume_id).first_or_404()
  resumelog = ResumeLog.query.filter_by(resume_id=resume_id)

  return render_template('resume.html', user=user, resume=resume, resumelog=resumelog)

@mainbp.route('/results/<user_id>/<resume_id>', methods=['GET'])
@login_required
def results (user_id,resume_id):
#using the current user's resume information as inputs for the resuem checker
  user = User.query.filter_by(user_id=current_user.user_id).first_or_404()
  resume = Resume.query.filter_by(resume_id=resume_id).first_or_404()
  resumes = Resume.query.filter_by(user_id=user_id)
  resumefile = open("website/" + resume.resumecontents, 'rb')
  results = get_results(resumefile)
  
  average = round((sum(results[1])/len(results[1])), 2)

  graphJSON = create_graph(results[0], results[1])

  #add result to resume log if it doesnt exist
  if(ResumeLog.query.filter_by(resume_id=resume_id).first() == None):
      newResumeLog = ResumeLog(user_id=current_user.user_id, resume_id=resume_id, result=average, keywords=to_JSON(results[0]), values=to_JSON(results[1]))
      db.session.add(newResumeLog)
      db.session.commit()

  return render_template('results.html', graphJSON=graphJSON, average=average, resume=resume, resumes=resumes)

@mainbp.route('/compare/<resume_id>/<compare_id>', methods=['GET'])
@login_required
def compare (resume_id,compare_id):
  resume = ResumeLog.query.filter_by(resume_id=resume_id).first_or_404()
  resumeToCompare = ResumeLog.query.filter_by(resume_id=compare_id).first_or_404()

  average = resume.result
  keywords = from_JSON(resume.keywords)
  values = from_JSON(resume.values)

  graphJSON = create_graph(keywords, values)

  compAverage = resumeToCompare.result
  compKeywords = from_JSON(resumeToCompare.keywords)
  compValues = from_JSON(resumeToCompare.values)

  compGraphJSON = create_graph(compKeywords, compValues)
  
  return render_template('compare.html', graphJSON=graphJSON, average=average, compGraphJSON=compGraphJSON, compAverage=compAverage, resume=resume, resumeToCompare=resumeToCompare)

def create_graph(keywords, scores):
  df = pd.DataFrame({
    "Keyword": keywords,
    "Score": scores
  })
  
  fig = px.bar(df, x="Score", y="Keyword", orientation="h")

  return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

#methods for saving lists into SQL
def to_JSON(lst):
    return json.dumps(lst).encode('utf8')

def from_JSON(data):
    return json.loads(data.decode('utf8'))
