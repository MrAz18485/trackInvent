from flask import Flask, render_template, request
# using sqlite for sql db
app = Flask(__name__)


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


@app.route("/login", methods=["POST", "GET"])
def index():
    return render_template("login.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        render_template("register.html")