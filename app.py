# with the help of https://flask.palletsprojects.com/en/3.0.x/tutorial/factory/

import os
from flask import Flask, render_template, request
# using sqlite for sql db
app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"



@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        render_template("register.html")

@app.route("/")
@login_required
def index():
    return render_template("index.html")