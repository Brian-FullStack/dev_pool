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


@app.route("/search_assets", methods=["GET", "POST"])
def search_assets():
    db_query = request.form.get("db_query")
    assets = list(mongo.db.assets.find({"$text": {"$search": db_query}}))
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
                existing_user["password"],
                    request.form.get("password")):
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


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    assets = list(mongo.db.assets.find(
        {"asset_creator": session["user"]}))
    return render_template("profile.html", username=username, assets=assets)


@app.route("/signOut")
def signOut():
    # Remove user from session variables
    session.pop("user")
    return redirect(url_for("signIn"))


@app.route("/create_asset", methods=["GET", "POST"])
def create_asset():
    if request.method == "POST":
        asset = {
            "category_name": request.form.get("category_name"),
            "asset_title": request.form.get("asset_title"),
            "asset_description": request.form.get("asset_description"),
            "asset_url": request.form.get("asset_url"),
            "date_added": request.form.get("date_added"),
            "asset_image": request.form.get("asset_image"),
            "asset_creator": session["user"]
        }
        mongo.db.assets.insert_one(asset)
        flash("Thank you for sharing {}, with Dev Pool".format(
            request.form.get("asset_title")))
        return redirect(url_for('get_assets'))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("create_asset.html", categories=categories)


@app.route("/edit_asset/<asset_id>", methods=["GET", "POST"])
def edit_asset(asset_id):
    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name"),
            "asset_title": request.form.get("asset_title"),
            "asset_description": request.form.get("asset_description"),
            "asset_url": request.form.get("asset_url"),
            "date_added": request.form.get("date_added"),
            "asset_image": request.form.get("asset_image"),
            "asset_creator": session["user"]
        }
        mongo.db.assets.update_one(
            {"_id": ObjectId(asset_id)}, {"$set": submit})
        flash("{} Updated Successfully".format(
            request.form.get("asset_title")))
        return redirect(url_for('get_assets'))

    asset = mongo.db.assets.find_one({"_id": ObjectId(asset_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template(
        "edit_asset.html", asset=asset, categories=categories)


@app.route("/delete_asset/<asset_id>")
def delete_asset(asset_id):
    mongo.db.assets.delete_one({"_id": ObjectId(asset_id)})
    flash("Asset has been sucessfully deleted!")
    return redirect(url_for("get_assets"))


@app.route("/list_categories")
def list_categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("categories.html", categories=categories)


@app.route("/create_category", methods=["GET", "POST"])
def create_category():
    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.insert_one(category)
        flash("New Category Added")
        return redirect(url_for("list_categories"))

    return render_template("create_category.html")


@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if request.method == "POST":
        submit_edit = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.update_one(
            {"_id": ObjectId(category_id)}, {"$set": submit_edit})
        flash("Category Successfully Edited")
        return redirect(url_for('list_categories'))

    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("edit_category.html", category=category)


@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    mongo.db.categories.delete_one({"_id": ObjectId(category_id)})
    flash("Successfully Deleted!")
    return redirect(url_for("list_categories"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
