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

  df = pd.DataFrame({
    "Keyword": results[0],
    "Score": results[1]
  })

  tip_values = check_conditions(df)
  
  average = round(df["Score"].mean(), 2)
  if(pd.isna(average)):
      average = 0

  graphJSON = create_graph(df)

  #add result to resume log if it doesnt exist
  if(ResumeLog.query.filter_by(resume_id=resume_id).first() == None):
      newResumeLog = ResumeLog(user_id=current_user.user_id, resume_id=resume_id, result=average, keywords=to_JSON(results[0]), values=to_JSON(results[1]))
      db.session.add(newResumeLog)
      db.session.commit()

  return render_template('results.html', graphJSON=graphJSON, average=average, resume=resume, resumes=resumes, tip_values=tip_values)

@mainbp.route('/compare/<resume_id>/<compare_id>', methods=['GET'])
@login_required
def compare (resume_id,compare_id):
  resume = ResumeLog.query.filter_by(resume_id=resume_id).first_or_404()
  resumeToCompare = ResumeLog.query.filter_by(resume_id=compare_id).first_or_404()

  #calculate the required values
  average = resume.result
  keywords = from_JSON(resume.keywords)
  values = from_JSON(resume.values)

  df = pd.DataFrame({
    "Keyword": keywords,
    "Score": values
  })

  tip_values = check_conditions(df)

  graphJSON = create_graph(df)

  compAverage = resumeToCompare.result
  compKeywords = from_JSON(resumeToCompare.keywords)
  compValues = from_JSON(resumeToCompare.values)

  compDf = pd.DataFrame({
    "Keyword": compKeywords,
    "Score": compValues
  })

  comp_tip_values = check_conditions(compDf)

  compGraphJSON = create_graph(compDf)
  
  return render_template('compare.html', graphJSON=graphJSON, average=average,
                         compGraphJSON=compGraphJSON, compAverage=compAverage,
                         resume=resume, resumeToCompare=resumeToCompare,
                         tip_values=tip_values, comp_tip_values=comp_tip_values)

def create_graph(df):
  
  fig = px.bar(df, x="Score", y="Keyword", orientation="h")

  return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

#check for conditions, to see which tips need to be given
def check_conditions(df):
  tip_values = []
  if(df[df["Score"] < 10].count()["Score"] >= 3):
      tip_values.append(1)
  if(df[df["Score"] < 5].count()["Score"] >= 1):
      tip_values.append(2)
  if(df[(df["Score"] > 20) & (df["Score"] > 40)].count()["Score"] >= 2):
      tip_values.append(3)
  if(df[(df["Score"] > 50)].count()["Score"] >= 1):
      tip_values.append(4)
  return tip_values

#methods for saving lists into SQL
def to_JSON(lst):
    return json.dumps(lst).encode('utf8')

def from_JSON(data):
    return json.loads(data.decode('utf8'))
