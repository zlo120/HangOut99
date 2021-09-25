from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.fields.simple import PasswordField
from wtforms.validators import *

class Register(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()], render_kw={"placeholder": "Enter email"})
    username = StringField("Username", validators=[InputRequired()], render_kw={"placeholder": "Enter username"})
    password = PasswordField("Password", validators=[InputRequired()], render_kw={"placeholder": "Enter password"})
    confirm = PasswordField("Confirm Password", validators=[InputRequired()], render_kw={"placeholder": "Confirm password"})
    submit = SubmitField("Register")

class Login(FlaskForm):
    username = StringField("Username", validators=[InputRequired()], render_kw={"placeholder": "Enter username"})
    password = PasswordField("Password", validators=[InputRequired()], render_kw={"placeholder": "Enter password"})
    submit = SubmitField("Login")

class Authenticate(FlaskForm):
    token = StringField("Authentication Code", validators=[InputRequired()], render_kw={"placeholder": "0000"})
    submit = SubmitField("Authenticate")

class CreateEvent(FlaskForm):
    title = StringField("Title *", validators=[InputRequired()], render_kw={"placeholder": "Name of the event"})
    description = TextAreaField("Description *", validators=[InputRequired()], render_kw={"rows":"10","placeholder": "Description of the event"})
    date = DateField("Date", validators=[InputRequired()] )
    time = TimeField("Time", validators=[InputRequired()] )
    submit = SubmitField("Submit")
