from functools import wraps
from flask import g, redirect, render_template

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function