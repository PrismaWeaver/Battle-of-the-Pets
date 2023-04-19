import os
import flask
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import requests
from os import getenv
from dotenv import load_dotenv, find_dotenv

app = Flask(__name__)
load_dotenv(find_dotenv())
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

# this will serve as the base for the recipe database

class Comment(db.Model): #a model for a row, defines a table
    id = db.Column(db.Integer, primary_key=True)
    movie = db.Column(db.Integer, unique=False, nullable=False)
    username = db.Column(db.String(80), unique=False, nullable=False)
    rating = db.Column(db.Integer, unique=False, nullable=False)
    comment = db.Column(db.String(420), unique=False, nullable=False)
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(420), nullable=False)

with app.app_context():
    db.create_all()


# the following is the base for the login screen

@app.route('/') #this initializes the movie
def start():
    return flask.render_template("login.html")

@app.route('/login', methods=["POST"])
def login():
    form_data = flask.request.form
    user = form_data["user"]
    unique = db.session.query(User).filter_by(username=user).first() is None
    if(unique):
        u = User(username=user)
        db.session.add(u)
        db.session.commit()
    return flask.redirect(flask.url_for("index", user=user))
    
    
# the following is the base for the recipe list screen

@app.route('/dash')
def index():
    pass
    #this page should display the user dashboard:
    #a searchbar at the top which redirects to the search page
    #a display of saved recipes list
    #maybe previous comments from the user

@app.route('/search/<id>') #id is for the index of the search
def search():
    #search should be passed via redirect
    #this is to keep the same search while navigating pages
    search = flask.request.args['search']
    
    #some code to break the search into blocks of 10? 20?
    #id refers to the num of blocks to incriment forward by when loading the page
    
    return flask.render_template("search.html", search=search, id=id)
    
    #these should be called by nav buttons on the search page:
    #for prev page
    # return flask.redirect(flask.url_for("search", search=search, id=id-1))
    #for next page
    # return flask.redirect(flask.url_for("search", search=search, id=id+1))

#this is a basic template for how to enter data into the DB
#and also a template for managing button interactions on the page
@app.route('/submit', methods=["POST"])
def submit():
    form_data = flask.request.form
    c = Comment(movie = form_data["movie"], 
                      username = form_data["user"],
                      rating = form_data["rating"],
                      comment = form_data["comment"])  
    db.session.add(c)
    db.session.commit()
    return flask.redirect(flask.url_for("index", user=form_data["user"]))

#app.run()
