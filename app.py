import flask
import os
import requests

from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from werkzeug.security import generate_password_hash, check_password_hash


# create the app
app = Flask(__name__)

# load environment variables and set app config settings
load_dotenv(find_dotenv())
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config['SECRET_KEY'] = getenv("SECRET_KEY")

# create database
db = SQLAlchemy(app)


# These classes form the relations in the database 
class Comment(db.Model): #a model for a row, defines a table
    id = db.Column(db.Integer, primary_key=True)
    movie = db.Column(db.Integer, unique=False, nullable=False)
    username = db.Column(db.String(80), unique=False, nullable=False)
    rating = db.Column(db.Integer, unique=False, nullable=False)
    comment = db.Column(db.String(420), unique=False, nullable=False)
    
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(420), nullable=False)


# make sure database tables are created
with app.app_context():
    db.create_all()

# setup user authentification
login_manager = LoginManager()
login_manager.init_app(app)

# this is how the login manager will be able to
# set who is logged in.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# Landing Page: If the user is logged in, go directly to the
# Dashboard, and if not go to the Login Page
@app.route('/')
def start():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))


# Login Page: from here they can login and be redirected to the Dashboard,
# or they can go to the create_account page.
@app.route('/login', methods=['GET','POST'])
def login():
    error = None
    # if they submitted the login form, check the username and password
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # get a user from the database
        user = User.query.filter_by(username=username).first()

        # if the user exists and the password matches, log them in
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('start'))
        # otherwise log an error message
        else:
            error = 'Invalid credentials. Please try again.'
        
    return render_template('login.html', error=error)


# Create Account: you can arrive here from the login page
# on this page you create a new acocunt to be stored in the database
@app.route('/create_account',methods=['GET','POST'])
def create_account():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # get user from the database
        user = User.query.filter_by(username=username).first()

        # if you were able to find a user, then log error
        if user:
            error = 'Account already exists. Try again.'
        # otherwise go back to the login page
        else:
            # hash the users password
            hashed_password = generate_password_hash(password)
            # save user credentials to the database
            new_user = User(username=username,password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return render_template('login.html')

    return render_template('create_account.html',error=error)

    
# the following is the base for the recipe list screen

@app.route('/dash')
@login_required
def index():
    pass
    #this page should display the user dashboard:
    #a searchbar at the top which redirects to the search page
    #a display of saved recipes list
    #maybe previous comments from the user

@app.route('/search/<id>') #id is for the index of the search
@login_required
def search():
    #search should be passed via redirect
    #this is to keep the same search while navigating pages
    search = request.args['search']
    
    #some code to break the search into blocks of 10? 20?
    #id refers to the num of blocks to incriment forward by when loading the page
    
    return render_template("search.html", search=search, id=id)
    
    #these should be called by nav buttons on the search page:
    #for prev page
    # return flask.redirect(flask.url_for("search", search=search, id=id-1))
    #for next page
    # return flask.redirect(flask.url_for("search", search=search, id=id+1))

#this is a basic template for how to enter data into the DB
#and also a template for managing button interactions on the page
@app.route('/submit', methods=["POST"])
@login_required
def submit():
    form_data = request.form
    c = Comment(movie = form_data["movie"], 
                      username = form_data["user"],
                      rating = form_data["rating"],
                      comment = form_data["comment"])  
    db.session.add(c)
    db.session.commit()
    return redirect(flask.url_for("index", user=form_data["user"]))

#app.run()
