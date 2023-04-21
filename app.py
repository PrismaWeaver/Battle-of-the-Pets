from dotenv import load_dotenv, find_dotenv
import flask
from flask import Flask, request, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
import os
from os import getenv
import requests

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

        # !!! will need to decrypt password when encription is added!!!
        user = User.query.filter_by(username=username,password=password).first()

        # if the username and password are incorrect, then mark error as true
        # and send them back to the login page
        if user == None:
            error = 'Invalid credentials. Please try again.'
        # otherwise, send to the dashboard
        else:
            login_user(user)
            return redirect(url_for('start'))
        
    return render_template('login.html', error=error)

@app.route('/create_account',methods=['GET','POST'])
def create_account():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username or email already exist
        # If so, render the template with an error message
        user = User.query.filter_by(username=username).first()
        if user != None:
            error = 'Account already exists. Try again.'
        # Otherwise, create the new account and redirect to a success page
        # (or log the user in automatically and redirect to the homepage)
        else:
            # !!!this needs to be hashed, will complete later!!!
            new_user = User(username=username,password=password)
            db.session.add(new_user)
            db.session.commit()
            return render_template('login.html')


    return render_template('create_account.html',error=error)

@app.route('/authenticate', methods=["POST"])
def autheticate():
    form_data = request.form
    user = form_data["user"]
    unique = db.session.query(User).filter_by(username=user).first() is None
    if(unique):
        u = User(username=user)
        db.session.add(u)
        db.session.commit()
    return redirect(url_for("index", user=user))
    
    
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
