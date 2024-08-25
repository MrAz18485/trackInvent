# with the help of https://flask.palletsprojects.com/en/3.0.x/tutorial/factory/
# https://www.geeksforgeeks.org/python-sqlite/ for helping me in sqlite
# https://stackoverflow.com/questions/28126140/python-sqlite3-operationalerror-no-such-table - helped me in solving a problem with connecting to the database (i.e. path issue)
# https://stackoverflow.com/questions/12075535/flask-login-cant-understand-how-it-works - helped me in creating a user class
# used flask-login for logging in, logging out and registering systems
# used flask-session for handling user sessions
import os
import hashlib
from flask import Flask, render_template, request, redirect, session, flash
from flask_session import Session
from flask_login import LoginManager, UserMixin
from helpers import login_required
import sqlite3
import uuid
# using sqlite for sql db

app = Flask(__name__)
app.secret_key = 'skIW!2&9GJ/!S,ab,R3Tv#c'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
login_manager = LoginManager()
Session(app)

# .update() only accepts byte-like objects, hence I converted password to bytes-like form using .encode()
def hashPassword(input):
    sha256 = hashlib.sha256()
    sha256.update(input)
    password_hash = sha256.hexdigest()
    return password_hash


@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        email = request.form.get("emailField")
        password = request.form.get("passwordField").encode()
        password_hash = hashPassword(password)
        BASE_PATH = os.path.abspath(os.path.dirname(__file__)) + "\db"
        db_path = os.path.join(BASE_PATH, "maindb.db")
        try:
            with sqlite3.connect(db_path) as db:
                cursor = db.cursor()
        # when an error occurs
        except sqlite3.Error:
            flash(f"Error while connecting to database, please try again later. {{ sqlite3.Error }}", "danger")
            return render_template("error.html")
        userInfo = cursor.execute("SELECT * FROM userinformation WHERE email = ? AND password = ?;", (email, password_hash))
        userInfo = userInfo.fetchone()

        # userInfo will return None if there's no records matching, hence trying to reach ith index will return a TypeError, so handling it this way.
        try:
            session["id"] = userInfo[0]
        except TypeError:
            flash("Invalid Email/Password", "danger")
            return render_template("login.html")
        
        # If everything's fine, we can assign email and passwords to the session
        session["email"] = email
        session["password"] = password_hash
        flash("Login successful! Redirecting to homepage", "success")
        return render_template("index.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        passwordConfirm = request.form.get("confirmPassword")
        if email == "":
            flash("Email field cannot be left blank!", "danger")
            return render_template("register.html")
        elif password != passwordConfirm:
            flash("Passwords do not match!", "danger")
            return render_template("register.html")
        elif password == "":
            flash("Password field cannot be blank!", "danger")
            return render_template("register.html")
        elif len(password) < 6:
            flash("Your password length must be at least 6 characters", "danger")
            return render_template("register.html")
        # if all tests are successful

        # checking the connection to db
        BASE_PATH = os.path.abspath(os.path.dirname(__file__)) + "\db"
        db_path = os.path.join(BASE_PATH, "maindb.db")
        try:
            with sqlite3.connect(db_path) as db:
                cursor = db.cursor()
        except sqlite3.Error:
            flash(f"Error while connecting to database, please try again later. {{ sqlite3.Error }}", "danger")
            return render_template("error.html")
        
        # okay now we're connected to the db, but what if this email has been used before for another account?               
        replica = cursor.execute("SELECT email FROM userinformation WHERE email = ?", [email])
        
        # fetchall returns a list
        if not len(replica.fetchall()) == 0: # if there's an existing record with the same email that user is currently trying to register with
            flash("An account already exists with this email!", "danger")
            return render_template("register.html")
        
        password_hash = hashPassword(password.encode())
        # session id must be unique, hence using uuid is logical here
        session["id"] = str(uuid.uuid4())
        print(session)
        
        # inserting the session id, email and hashed password into the db
        cursor.execute("INSERT INTO userinformation VALUES (?, ?, ?);", (session["id"], email, password_hash))
        db.commit()
        flash("Registration successful! You can login with your registered email and password", "success")
        return render_template("login.html")

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    flash("Successfully logged out!", "success")
    return render_template("login.html")

app.run(debug=True)
