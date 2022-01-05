import os
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


# Configure the database name
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
# Configure the connection string/MONGO_URI
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
# Configure the SECRET_KEY
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_assets")
def get_assets():
    assets = mongo.db.assets.find()
    return render_template('assets.html', assets=assets)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Check if user already exists in the db
        existing_user = mongo.db.users.find_one(
           {"username": request.form.get("username").lower()})

        # If username exists then display that to the user and refresh the page
        if existing_user:
            flash("Sorry, that username already exists.")
            redirect(url_for("register"))

        # Create a dictionary from the user inputs
        new_user = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(new_user)

        # Place the user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
    return render_template("register.html")

@app.route("/signIn", methods=["GET", "POST"])
def signIn():
    return render_template("signin.html")

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
