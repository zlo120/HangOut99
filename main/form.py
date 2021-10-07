from typing import Sized
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, TextAreaField, FileField
from flask_wtf.file import FileRequired, FileField, FileAllowed
from wtforms.fields.core import BooleanField, IntegerField, SelectField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.fields.simple import PasswordField
from wtforms.validators import *
from datetime import datetime

from .models import Event
from .utils import user_loader, getUserGroups

# choices = [(data, display)]

def groups(current_user):
    this_user = user_loader(current_user.get_id())

    user_groups = getUserGroups(this_user.ID)

    groups = []

    for row in user_groups:
        groups.append(row)

    if groups == []:
        
        return [("You need to be in a group first", "You need to be in a group first")]

    return_this = []

    for group in groups:
        return_this.append((group[1], group[1]))

    return return_this

def createEditForm(current_user, event):
    class CreateEvent(FlaskForm):
        title = StringField("Title *", validators=[InputRequired()], render_kw={"placeholder": "Name of the event", "value" : event.Name})
        description = TextAreaField("Description *", validators=[InputRequired()], render_kw={"rows":"10","placeholder": "Description of the event"})
        date = DateField("Date", validators=[Optional()])
        time = TimeField("Time", validators=[Optional()])
        location = StringField("Location address", validators=[Optional()], render_kw={"placeholder": "Location address"})
        group = SelectField("Hangout Group", choices=groups(current_user))
        submit = SubmitField("Submit")

    return CreateEvent() 

def createEventForm(current_user):
    class CreateEvent(FlaskForm):
        title = StringField("Title *", validators=[InputRequired()], render_kw={"placeholder": "Name of the event"})
        description = TextAreaField("Description *", validators=[InputRequired()], render_kw={"rows":"10","placeholder": "Description of the event"})
        date = DateField("Date", validators=[Optional()])
        time = TimeField("Time", validators=[Optional()])
        group = SelectField("Hangout Group", choices=groups(current_user))
        location = StringField("Location address", validators=[Optional()], render_kw={"placeholder": "Location address"})
        submit = SubmitField("Submit")

    return CreateEvent()

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

class CreateGroup(FlaskForm):
    name = StringField ("Name *", validators=[InputRequired()], render_kw={"placeholder": "Name of the group"} )
    pin = IntegerField("Pin (optional)", validators=[Optional()], render_kw={"placeholder": "Create a pin for others to join"})
    submit = SubmitField("Create")

class JoinGroup(FlaskForm):
    name = StringField ("Name *", validators=[InputRequired()], render_kw={"placeholder": "Name of the group"} )
    pin = IntegerField ("Pin *", validators=[InputRequired()], render_kw={"placeholder": "Pin"} )
    submit = SubmitField("Submit")

def editGroup(group):

    class EditGroup(FlaskForm):
        name = StringField ("Name *", validators=[InputRequired()], render_kw={"value" : group.Name, "placeholder": "Name of the group"} ) 
        pin = IntegerField("Pin (optional)", validators=[Optional()], render_kw={"value" : group.Pin,"placeholder": "Pin (optional)"})
        submit = SubmitField("Submit")

    return EditGroup()

ALLOWED_FILE = {'PNG','JPG','png','jpg', 'JPEG', 'jpeg'}

class UploadImage(FlaskForm):
    image = FileField('Destination Image', validators=[FileRequired(), FileAllowed(ALLOWED_FILE)])
    submit = SubmitField("Upload")

class CreateComment(FlaskForm):
    comment = StringField ("Name *", validators=[InputRequired(), Length(max = 256)], render_kw={"placeholder": "Comment"} ) 
    submit = SubmitField("Post")