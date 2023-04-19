from dotenv import load_dotenv, find_dotenv
import flask
from flask import Flask
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


# this will serve as the base for the recipe database

class Recipe_Comments(db.Model): #a model for a row, defines a table
    id = db.Column(db.Integer, primary_key=True)
    recipe = db.Column(db.Integer, unique=False, nullable=False)
    user = db.Column(db.String(80), unique=False, nullable=False)
    rating = db.Column(db.Integer, unique=False, nullable=False)
    comment = db.Column(db.String(420), unique=False, nullable=False)
    
class Saved_Recipes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(80), unique=False, nullable=False)
    recipe = db.Column(db.Integer, unique=False, nullable=False)
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(420), nullable=False)

# make sure sql alchemy tables are created
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


# the following is the base for the login screen

@app.route('/') #this initializes the movie
def index():
    #if user is not logged in:
    return flask.render_template("login.html")
    #else, display the following:
    #this page should display the user dashboard
    #a searchbar at the top which redirects to the search page
        #this should call the search() function directly below
    #a display of saved recipes list
        #query = db.session.query(Saved_Recipes).filter_by(user=current_user).all()
    #maybe previous comments from the user
        #query = db.session.query(Recipe_Comments).filter_by(user=current_user).all()
    #the saved recipe list should have buttons next to each recipe that allows the user
    #to add said recipe to a shopping list (could be part of the DB, but should be deleted after use), array could work better

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
    
@app.route('/submit', methods=['POST'])
def search():
    load_dotenv(find_dotenv())
    form_data = flask.request.form
    SPOON_API_SEARCH_URL = "https://api.spoonacular.com/recipes/complexSearch?"
    spoon_api_response = requests.get(
        SPOON_API_SEARCH_URL,
        params={
            "apiKey": getenv("RECIPE_API"),
            "query": form_data["query"]
        },
    )
    results = spoon_api_response.json()
    return flask.redirect(flask.url_for("search_results", results=results, indi=0))

@app.route('/search/<indi>') #indi is for the index of the search
def search_results():
    #search should be passed via redirect
    #this is to keep the same search while navigating pages
    results = flask.request.args['results']
    indi = flask.request.args['indi']
    if(indi < 0): indi = 0
    
    #some code to break the search into blocks of 10? 20?
    #indi refers to the num of blocks to incriment forward by when loading the page
    
    return flask.render_template("search.html", results=results, indi=indi)
    #should a user click on the name of a recipe, its should redirect them to:
        # url/<recipe id>
    #these should be called by nav buttons on the search page:
    #for prev page
        #return flask.redirect(flask.url_for("search_results", results=results, indi=indi-1))
    #for next page
        #return flask.redirect(flask.url_for("search_results", results=results, indi=indi+1))

@app.route('/<recipe>')
def recipe():
    recipe = flask.request.args['recipe']
    #if the recipe info isnt in the redirect, you can fetch it like this
    SPOON_API_GET_INFO = 'https://api.spoonacular.com/recipes/'
    spoon_api_response = requests.get(
        SPOON_API_GET_INFO + recipe + '/information',
        params={
            "apiKey": getenv("RECIPE_API"),
        },
    )
    recipe = spoon_api_response
    return flask.render_template("recipe.html", recipe=recipe)

@app.route('/<recipe>/submit', methods=["POST"])
def submit():
    recipe = flask.request.args['recipe']
    form_data = flask.request.form
    c = Recipe_Comments(recipe['id'], 
                      user = form_data["user"],
                      rating = form_data["rating"],
                      comment = form_data["comment"])  
    db.session.add(c)
    db.session.commit()
    return flask.redirect(flask.url_for("recipe", recipe=recipe))

#app.run()
