from flask import Blueprint, redirect, render_template, session, request, flash, url_for
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from flask_wtf import FlaskForm

from . import bcrypt, db
from .utils import createDateTimeObject, send_email
from .models import User, Token
from .form import Authenticate, Register, Login

import csv, random

userbp = Blueprint("user", __name__, url_prefix="/user")

# Authenticate
@userbp.route('/authenticate', methods=['GET', 'POST'])
def authenticate():

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = Authenticate()
    if form.validate_on_submit():
        token = request.form['token']

        confirmedToken = Token.query.filter_by(UserToken = token).first()

        if confirmedToken:
            # Update user row IsValidated to True
            user = User.query.filter_by(Email=confirmedToken.Email).first()
            user.IsValidated = True

            db.session.add(user)
            db.session.commit()

            # Remove token from db
            db.engine.execute(f"DELETE FROM tokens WHERE Email = '{confirmedToken.Email}'")

            # Then log the user in
            login_user(user, remember = True)

            flash("You are now logged in!")
            return redirect(url_for('main.index'))

        else:
            flash("Your authentication code is incorrect")
            return redirect(url_for('user.authenticate'))
    return render_template('user/authenticate.html', form = form)

# User

# Register
@userbp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = Register()

    if form.validate_on_submit():
        form_username = request.form['username']
        form_email = request.form['email']
        form_pwd = request.form['password']
        form_cpwd = request.form['confirm']

        # Make some checks
        if form_pwd != form_cpwd:
            flash("Your confirmation password didn't match")
            return redirect(url_for('register'))

        u_exists = User.query.filter_by(Username=form_username).first() is not None
        e_exists = User.query.filter_by(Email=form_email).first() is not None

        if e_exists:
            flash("That email already exists")
            return redirect(url_for('user.register'))

        if u_exists:
            flash("That username already exists")
            return redirect(url_for('user.register'))

        user = User(
            Email = form_email,
            Username = form_username,
            Password = bcrypt.generate_password_hash(form_pwd).decode('utf-8'),
            IsValidated = False
        )

        db.session.add(user)
        db.session.commit()

        token = random.randint(1000,9999)

        # Store the token        
        token_obj = Token (
            Email = form_email,
            UserToken = token            
        )

        db.session.add(token_obj)
        db.session.commit()

        # send_email(token, form_email)

        login_user(user, remember = True)
        flash("You are now logged in!")
        return redirect(url_for('main.index'))

    return render_template("user/register.html", form = form)

@userbp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = Login()

    if form.validate_on_submit():
        username = request.form['username']
        pwd = request.form['password']

        # Authenticate
        user = User.query.filter_by(Username = username).first()

        if user == None:
            flash("An account with that username doesn't exist")
            return redirect(url_for('user.login'))

        if user.Username == username and bcrypt.check_password_hash(user.Password, pwd):
            login_user(user, remember = True)
            flash("You are now logged in!")
            return redirect(url_for('main.index'))
        else:
            flash("Incorrect password")
            return redirect(url_for('login'))

    return render_template("user/login.html", form = form)

@userbp.route('/user/logout')
@login_required
def logout():
    logout_user()
    flash("You are now logged out")
    return redirect(url_for('main.index'))

@userbp.route('/send')
def send():
    token = str(random.randint(1000,9999))
    send_email(token, "zachary.lo200@gmail.com", False)

    return "sent"

@userbp.route('/user-id/<user>')
def user(user):
    return user