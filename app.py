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
        # After successful registration, bring user to their profile page
        return redirect(url_for(
            "profile", username=session["user"]))

    return render_template("register.html")


@app.route("/signIn", methods=["GET", "POST"])
def signIn():
    if request.method == "POST":
        # Check if user already exists in the db
        existing_user = mongo.db.users.find_one(
           {"username": request.form.get("username").lower()})

        if existing_user:
            # If user exists, check password matches hashed password
            # Display a message
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome back {}, ".format(
                        request.form.get("username")))
                    return redirect(url_for(
                        "profile", username=session["user"]))
            else:
                # If password doesn't match display a message to the user
                flash("Incorrect Username or Password")
                redirect(url_for("signIn"))
        else:
            flash("Incorrect Username or Password")
            redirect(url_for("signIn"))

    return render_template("signin.html")



@app.route("/profile/<username>")
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    return render_template("profile.html", username=username)


@app.route("/signOut")
def signOut():
    # Remove user from session variables
    session.pop("user")
    return redirect(url_for("signIn"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
