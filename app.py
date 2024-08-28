# with the help of https://flask.palletsprojects.com/en/3.0.x/tutorial/factory/
# https://www.geeksforgeeks.org/python-sqlite/ for helping me in sqlite
# https://stackoverflow.com/questions/28126140/python-sqlite3-operationalerror-no-such-table - helped me in solving a problem with connecting to the database (i.e. path issue)
# https://stackoverflow.com/questions/12075535/flask-login-cant-understand-how-it-works - helped me in creating a user class
# used flask-login for logging in, logging out and registering systems
# used flask-session for handling user sessions
# https://stackoverflow.com/questions/57963502/how-do-i-update-my-css-stylesheet-saved-under-static-folder-for-python-flask-web - Helped me to figure out a way to establish
# communication between flask and python

# Used https://www.reddit.com/r/cs50/comments/v3s2f6/is_everything_submitted_to_a_flask_form_a_string/ in function, additem, to convert the variable "itemcount"
# from string form to int form in request.form.get instead of typecasting it like int()

import os
import hashlib
import datetime
from flask import Flask, render_template, request, redirect, session, flash
from flask_session import Session
from flask_login import LoginManager, UserMixin
from helpers import login_required
from forms import settingsForm
import sqlite3
import uuid
# using sqlite for sql db

app = Flask(__name__)
app.secret_key = 'skIW!2&9GJ/!S,ab,R3Tv#c'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
login_manager = LoginManager()
Session(app)

# Setting these two as global variables since I'll use them through many functions in my program, hence instead of defining them for each function I'd rather
# define them here.
BASE_PATH = os.path.abspath(os.path.dirname(__file__)) + "\db"
db_path = os.path.join(BASE_PATH, "maindb.db")

# .update() only accepts byte-like objects, hence I converted password to bytes-like form using .encode()
def hashPassword(input):
    sha256 = hashlib.sha256()
    sha256.update(input)
    password_hash = sha256.hexdigest()
    return password_hash

def loadInventory(id):
    # decided to convert this to a function since I'll be using this logic more than once, to avoid copy-paste
    try:
        with sqlite3.connect(db_path) as db:
            cursor = db.cursor()
    except sqlite3.Error as currentError:
        flash(f"Error while retrieving user inventory from database { currentError } ", "danger")
    userinventory = cursor.execute("SELECT * FROM inventory WHERE userid = ?", [id])

    # using .fetchall() more than once in a single cursor causes a lot of problems such as data not being shown although being existent due to its nature
    userinventory = userinventory.fetchall()

    # if no items exist in the inventory
    if len(userinventory) == 0:
        return None
    
    return userinventory


# to make things more convenient
def updateInventory(cursor, db, values):
    # first query, without any updates
    userinventory = loadInventory(session["id"])
    try:     
        # 3 possible scenarios here
        if values[0] == "UPDATE":
            cursor.execute("UPDATE inventory SET count = ? WHERE userid = ? AND item = ?;", (values[3], values[1], values[2]))
        elif values[0] == "INSERT":
            cursor.execute("INSERT INTO inventory VALUES(?, ?, ?);", (values[1], values[2], values[3]))
        elif values[0] == "DELETE":
            cursor.execute("DELETE FROM inventory WHERE userid = (?) AND item = ?;", (values[1], values[2]))
        # new data added to the db, hence .commit() is necessary
        db.commit()
        # second query, values are now updated, hence updated values should be shown to the user
        userinventory = loadInventory(session["id"])
        return userinventory
    except sqlite3.Error as currentError:
        flash(f"Error while connecting to database, please try again later. { currentError }", "danger")
        return None

def updateLogs(itemname, count):
    logTime = datetime.datetime.now()
    try:
        with sqlite3.connect(db_path) as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO logs VALUES(?, ?, ?, ?);", (session["id"], itemname, count, logTime))
            db.commit()
            return True
    except sqlite3.Error as currentError:
        flash(f"Error while saving log for database { currentError } ", "danger")
        return None

# https://www.geeksforgeeks.org/python-program-to-sort-a-list-of-tuples-by-second-item/ - used for figuring out the logic at sorting list of tuples
def sort_tuple(tup, keyIndex):

    # orders tuples by (keyIndex)th item (i.e. count) in each tuple, with the help of lambda function
    # example: if keyIndex = 2, then tuples will be ordered by the second item in descending order
    tup.sort(reverse = True, key = lambda x: x[keyIndex])
    return tup

@app.route("/")
@login_required
def inventory():

    # ordering list of tuples before passing it as an argument to render_template. You can read the description of sort_tuple for a deeper understanding
    userinventory = sort_tuple(loadInventory(session["id"]), 2)
    return render_template("inventory.html", items=userinventory, itemsTableVisible = True)


@app.route("/additem", methods=["GET", "POST"])
@login_required
def additem():

    # okay, this is the inventory RIGHT AFTER loading the page (i.e. no changes have been made)
    userinventory = sort_tuple(loadInventory(session["id"]), 2)
    if request.method == "GET":
        return render_template("additem.html", items=userinventory, itemsTableVisible = True)
    else:
        itemName = request.form.get("nameField")

        # typecasting since request.form.get returns a string
        itemCount = request.form.get("countField", type=int)
        if (itemCount is None or itemCount <= 0):
            flash("Item count cannot be less than 1!", "danger")
            return render_template("additem.html", items=userinventory, itemsTableVisible = True)
        
        # Trying to connect to the db
        try:
            with sqlite3.connect(db_path) as db:
                cursor = db.cursor()
        except sqlite3.Error as currentError:
            flash(f"Error while connecting to database, please try again later. { currentError }", "danger")
            return render_template("additem.html", items=userinventory, itemsTableVisible = True)
        
        # looping through userinventory to see if item name exists, if so updating the existing item count is sufficient
        if (userinventory != None):
            for row in userinventory:
                print(row)
                # ('id', 'itemname', 'itemcount')
                if row[1] == itemName:
                    existingItemCount = row[2]
                    vals = ["UPDATE", session["id"], itemName, existingItemCount + itemCount]
                    updatedInventory = sort_tuple(updateInventory(cursor, db, vals), 2)

                    # kind of repetitive, voids the "Don't repeat yourself" principle. Might find a better way of solving this.
                    if (updatedInventory != None):

                        # when update is successful, log it to the db
                        updateLogs(vals[2], vals[3])
                        return render_template("additem.html", items=updatedInventory, itemsTableVisible = True)
                    else:
                        return render_template("additem.html", items=userinventory, itemsTableVisible = True)

        # if no records of the matching item is found OR userinventory doesn't consist of any items (i.e. userinventory = None, user doesnt have anything)
        vals = ["INSERT", session["id"], itemName, itemCount]
        updatedInventory = sort_tuple(updateInventory(cursor, db, vals), 2)
        if (updatedInventory != None):

            # when update is successful, log it to the db
            updateLogs(vals[2], vals[3])
            flash("Successfully applied changes!", "success")
            return render_template("additem.html", items=updatedInventory, itemsTableVisible = True)
        else:
            flash("There was an error while applying your request, please try again later.", "primary")
            return render_template("additem.html", items=userinventory, itemsTableVisible = True)

@app.route("/deleteitem", methods=["POST", "GET"])
@login_required
def deleteitem():

    # this function is pretty similar to function additem(), there's similar checks and error handling procedures.
    userinventory = sort_tuple(loadInventory(session["id"]), 2)
    print(userinventory)
    if request.method == "GET":
        return render_template("deleteitem.html", items=userinventory, itemsTableVisible = True)
    else:
        itemName = request.form.get("nameField")
        itemCount = request.form.get("countField", type=int)

        # trying to connect to the db to retrieve user's inventory
        try:
            with sqlite3.connect(db_path) as db:
                cursor = db.cursor()
        except sqlite3.Error as currentError:
            flash(f"Error while connecting to database, please try again later. { currentError }", "danger")
            return render_template("deleteitem.html", items=userinventory, itemsTableVisible = True)
        
        # number of items in db with the name {itemName}
        dbItemCount = 0
        for item in userinventory:
            if item[1] == itemName:
                dbItemCount = item[2]

        if (itemCount is None or itemCount <= 0):
            flash("Item count cannot be less than 1!", "danger")
            return render_template("deleteitem.html", items=userinventory, itemsTableVisible = True)
        elif (itemCount > dbItemCount):
            flash("Item count cannot be more than the number of items you currently hold!", "danger")
            return render_template("deleteitem.html", items=userinventory, itemsTableVisible = True)
        
        vals = []
        # if the number of items I want to delete equals the number of items I hold (for a single item), then delete the whole record itself
        if (itemCount == dbItemCount):
            vals = ["DELETE", session["id"], itemName, itemCount]
        # otherwise, update current count as (current record - itemcount)
        else:
            vals = ["UPDATE", session["id"], itemName, dbItemCount-itemCount]
        updatedInventory = sort_tuple(updateInventory(cursor, db, vals), 2)

        # if there's no errors, i.e. updateInventory() doesn't return none, render temp. with updated inventory
        if (updatedInventory != None):

            # same procedure as the one in function additem
            updateLogs(vals[2], -vals[3])
            flash("Successfully applied changes!", "success")
            return render_template("deleteitem.html", items=updatedInventory, itemsTableVisible = True)
        else:
            flash("There was an error while applying your request, please try again later.", "primary")
            return render_template("deleteitem.html", items=userinventory, itemsTableVisible = True)

@app.route("/history", methods=["GET"])
@login_required
def retrieveHistory():
    if request.method == "GET":
        try:
            with sqlite3.connect(db_path) as db:
                cursor = db.cursor()
        except sqlite3.Error as currentError:
            flash(f"Error while retrieving history from database { currentError } ", "danger")
            return render_template("history.html")
        print(session["id"])
        logs = sort_tuple(cursor.execute("SELECT * FROM logs WHERE userid = ?;", [session["id"]]).fetchall(), 3)
        print(logs)
        # not going to check whether if logs exist or not, even if it returns none, user should see the empty table of logs
        return render_template("history.html", logs=logs, itemsTableVisible = False, historyTableVisible = True)


# took some help from GPT here, especially for the line "option1 = settingsForm.ThemeOption.data"
@app.route("/settings", methods=["GET"])
@login_required
def adjustSetting():
    form = settingsForm()
    if request.method == "GET":
        return render_template("settings.html", itemsTableVisible = False, historyTableVisible = False, form=form)

@app.route("/login", methods=["POST", "GET"])
def login():

    # start off with a fresh session
    session.clear()

    if request.method == "GET":
        return render_template("login.html")
    else:
        email = request.form.get("emailField")
        password = request.form.get("passwordField").encode()
        password_hash = hashPassword(password)
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

        # flash("Login successful! Redirecting to homepage", "success")

        userinventory = sort_tuple(loadInventory(session["id"]), 2)
        flash("Successfully logged in!", "primary")
        return render_template("inventory.html", items=userinventory, itemsTableVisible = True)


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
            flash(f"Error while connecting to database, please try again later. { sqlite3.Error }", "danger")
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
        flash("Registration successful! You can login with your registered email and password", "primary")

        # right after registration, user will not have any items, so parameter should be set to None
        return render_template("inventory.html", items=None, itemsTableVisible = True)

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    flash("Successfully logged out!", "primary")
    return render_template("login.html")

app.run(debug=True)
