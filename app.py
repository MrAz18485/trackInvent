# with the help of https://flask.palletsprojects.com/en/3.0.x/tutorial/factory/
# https://www.geeksforgeeks.org/python-sqlite/ for helping me in sqlite
# https://stackoverflow.com/questions/28126140/python-sqlite3-operationalerror-no-such-table - helped me in solving a problem with connecting to the database (i.e. path issue)

# used flask-login for logging in, logging out and registering systems
import os
import hashlib
from flask import Flask, render_template, request, redirect, session, flash
from flask_session import Session
from flask_login import LoginManager
from helpers import login_required
import sqlite3
# using sqlite for sql db

app = Flask(__name__)
app.secret_key = 'skIW!2&9GJ/!S,ab,R3Tv#c'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
login_manager = LoginManager()
login_manager.init_app(app)

def connectDB():
    BASE_PATH = os.path.abspath(os.path.dirname(__file__)) + "\db"
    db_path = os.path.join(BASE_PATH, "maindb.db")
    print(db_path)
    try:
        with sqlite3.connect(db_path) as db:
            cursor = db.cursor()
    except sqlite3.Error:
        flash("Error while connecting to database, please try again later", "error")
        return render_template("error.html")

# .update() only accepts byte-like objects, hence I converted password to bytes-like form using .encode()
def hashPassword(input):
    sha256 = hashlib.sha256()
    sha256.update(session["password"])
    password_hash = sha256.hexdigest()
    return password_hash


@LoginManager

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        session["email"] = request.form.get("emailField")
        session["password"] = request.form.get("passwordField").encode()

        password_hash = hashPassword(session["password"])

        BASE_PATH = os.path.abspath(os.path.dirname(__file__)) + "\db"
        db_path = os.path.join(BASE_PATH, "maindb.db")
        print(db_path)
        try:
            with sqlite3.connect(db_path) as db:
                cursor = db.cursor()
        except sqlite3.Error:
            flash("Error while connecting to database, please try again later", "error")
            return render_template("error.html")
        userInfo = cursor.execute("SELECT * FROM userinformation WHERE email = ? AND password = ?", session["email"], [password_hash])
        if len(userInfo.fetchall()) == 0: # when there's no records that match
            flash("Invalid Email/Password", "error")
            return render_template("login.html")
        else:
            return render_template("index.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        print(session["id"])
        email = request.form.get("email")
        password = request.form.get("password")
        passwordConfirm = request.form.get("confirmPassword")
        print(password + "-" + passwordConfirm)
        if email == "":
            flash("Email field cannot be left blank!", "error")
            return render_template("register.html")
        elif password != passwordConfirm:
            flash("Passwords do not match!", "error")
            return render_template("register.html")
        elif password == "":
            flash("Password field cannot be blank!", "error")
            return render_template("register.html")
        elif len(password) < 6:
            flash("Your password length must be at least 6 characters", "error")
            return render_template("register.html")
        # if all tests are successful

        # checking the connection to db
        BASE_PATH = os.path.abspath(os.path.dirname(__file__)) + "\db"
        db_path = os.path.join(BASE_PATH, "maindb.db")
        try:
            with sqlite3.connect(db_path) as db:
                cursor = db.cursor()
        except sqlite3.Error:
            flash("Error while connecting to database, please try again later.", "error")
            return render_template("error.html")
        # okay now we're connected to the db, but what if this email has been used before for another account?               
        replica = cursor.execute("SELECT email FROM userinformation WHERE email = ?", [email])
        if not len(replica.fetchall()) == 0: # if there's an existing record with the same email that user is currently trying to register with
            flash("An account already exists with this email!", "error")
            return render_template("register.html")
        
        password_hash = hashPassword(password)
        cursor.execute("INSERT INTO userinformation (id, email, password) VALUES (?, ?, ?)", session["id"], email, password)
        db.commit()
        flash("Registration successful! You can login with your registered email and password")
        return render_template("login.html")
app.run(debug=True)