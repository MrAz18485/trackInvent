from flask import Flask
# using sqlite for sql db
app = Flask(__name__)


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        render_template("register.html")