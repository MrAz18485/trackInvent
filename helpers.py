# with the help of https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
# and PS 9 - Finance, helpers.py
# At first I thought I could use flask-login but it didn't work the way I intended it to and setting it up for my current project was taking way longer than expected
# hence I decided not to use it, since I already have the necessary tools for my project.

from functools import wraps
from flask import session, request, redirect, url_for

# this function is the same function that's been used in PSET9 - Finance, helpers.py, login_required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("id") is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function