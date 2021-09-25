from flask import render_template, session, flash, redirect, url_for, request
from flask.blueprints import Blueprint
from flask_login import current_user, login_manager, login_user
from flask_login.utils import login_required, login_user, logout_user
from . import app, bcrypt, db, login_manager
from .models import User
from .form import CreateEvent

from datetime import datetime

# Load in user
@login_manager.user_loader
def load_user(email):
    return User.query.filter_by(Email = email).first()

mainbp = Blueprint('main', __name__)

# Main
@mainbp.route('/')
def index():
    user = None

    if current_user.is_authenticated:
        user = User.query.filter_by(Email = current_user.Email).first()

    return render_template("index.html", User = user)