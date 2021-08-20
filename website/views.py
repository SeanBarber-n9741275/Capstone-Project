from flask import Blueprint, render_template, request, session, url_for
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