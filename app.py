# with the help of https://flask.palletsprojects.com/en/3.0.x/tutorial/factory/
# https://www.geeksforgeeks.org/python-sqlite/ for helping me in sqlite

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
        session["password"] = request.form.get("passwordField")
        hashing = hashlib.sha256()
        hashing.update(session["password"])
        password_hash = hashing.hexdigest()
        conn = sqlite3.connect("userinfo.db")
        cursor = conn.cursor()
        userInfo = cursor.execute("SELECT * FROM userinfo WHERE password = ?", password_hash)
        print(userInfo)
        if len(userInfo) == 0:
            flash("Username or password does not exist!")
            return render_template("login.html")
        return render_template("index.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")