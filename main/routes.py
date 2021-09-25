from main import hangout
from flask import render_template, session, flash, redirect, url_for, request
from flask.blueprints import Blueprint
from flask_login import current_user, login_manager, login_user
from flask_login.utils import login_required, login_user, logout_user
from . import app, bcrypt, db, login_manager
from .models import User, HangOutGroup
from .form import CreateEvent

from datetime import datetime

# Load in user
@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(ID = id).first()

mainbp = Blueprint('main', __name__)

# CODE SNIPPETS

#       This returns a list of every user in the group called "Chiller"
#  User.query.filter(User.hangoutgroup.any(Name = "Chiller")).all()

#       This returns a kust of every user in the group called "Chiller"
# HangOutGroup.query.filter_by(Name = "Chiller").first().Users

#       BOTH RETURN THE SAME THING

# Main
@mainbp.route('/')
def index():
    user = None
    this_user = load_user(current_user.get_id())

    if current_user.is_authenticated:
        user = User.query.filter_by(Email = current_user.Email).first()

    return render_template("index.html", User = user)