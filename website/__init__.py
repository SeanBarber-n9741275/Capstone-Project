from flask import Flask, Response, redirect
from flask.helpers import url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db=SQLAlchemy()

#create a function that creates a web application
# a web server will run this web application
def create_app():
  
    app=Flask(__name__)  # this is the name of the module/package that is calling this app
    app.debug=True
    app.secret_key='anythingilike'

    #set the app configuration data 
    app.config['UPLOAD_FOLDER'] = '/static/image'
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///appdatabase.sqlite'
    
    #initialize db with flask app
    db.init_app(app)

    bootstrap = Bootstrap(app)

    #initialize the login manager
    login_manager=LoginManager()
    #set the name of the login function that lets user login
    #auth.login (blueprintname.viewfunction name)
    login_manager.login_view='auth.login' 
    login_manager.init_app(app)

    #create a user loader function takes userid and returns User
    from .models import User #importing here to avoid circular references
    @login_manager.user_loader 
    def load_user(user_id):
        return User.query.get(int(user_id))

    from website import views, auth
    app.register_blueprint(views.mainbp)
    app.register_blueprint(auth.bp)


    return app


