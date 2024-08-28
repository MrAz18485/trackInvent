from flask_wtf import FlaskForm
from wtforms import RadioField


class settingsForm(FlaskForm):
    themeOption = RadioField("Theme", choices=[("dark", "Dark"), ("normal", "Normal")])
    