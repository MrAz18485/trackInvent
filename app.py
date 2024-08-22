# with the help of https://flask.palletsprojects.com/en/3.0.x/tutorial/factory/
# https://www.geeksforgeeks.org/python-sqlite/ for helping me in sqlite
# https://stackoverflow.com/questions/28126140/python-sqlite3-operationalerror-no-such-table - helped me in solving a problem with connecting to the database (i.e. path issue)
import os
import hashlib
from flask import Flask, render_template, request, redirect, session, flash
from flask_session import Session
from helpers import login_required
import sqlite3
# using sqlite for sql db
app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


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
        sha256 = hashlib.sha256()

        # .update() only accepts byte-like objects, hence I converted password to bytes-like form using .encode()
        sha256.update(session["password"])
        password_hash = sha256.hexdigest()
        print(password_hash)

        try:
            BASE_PATH = os.path.abspath(os.path.dirname(__file__)) + "\db"
            db_path = os.path.join(BASE_PATH, "maindb.db")
            print(db_path)
            with sqlite3.connect(db_path) as db:
                cursor = db.cursor()
        except sqlite3.Error:
            error = sqlite3.Error
            return render_template("error.html")
        userInfo = cursor.execute("SELECT * FROM userinformation WHERE password = ?", [password_hash])
        print(userInfo.fetchone())
        if userInfo.fetchone() == None:
            error = "Invalid Email/Password"
            return render_template("login.html")
        else:
            return render_template("index.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        passwordConfirm = request.form.get("confirmPassword")
        if password != passwordConfirm:
            error = "Passwords do not match!"
            return render_template("register.html")
        return render_template("login.html")
app.run(debug=True)