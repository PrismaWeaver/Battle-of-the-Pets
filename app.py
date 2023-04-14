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
    
@app.route('/index')
def index():
    user = flask.request.args['user']
    missing = db.session.query(User).filter_by(username=user).first() is None
    if (missing):
        return flask.redirect(flask.url_for('start'))
    movie_id = get_rand_movie_id()
    movie = get_rand_movie(movie_id)
    query = db.session.query(Comment).filter_by(movie=movie_id).all()
    return flask.render_template("index.html", movie_id=movie_id, movie=movie, query=query, user=user)

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