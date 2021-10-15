from flask import Blueprint, redirect, render_template, session, request, flash, url_for
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from flask_wtf import FlaskForm

from . import bcrypt, db
from .utils import createDateTimeObject, send_email
from .models import User, Event, HangOutGroup
from .form import Register, Login, DeleteGroup, DeleteEvent, editUser

import csv, random

userbp = Blueprint("user", __name__, url_prefix="/user")

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
            return redirect(url_for('user.register'))

        u_exists = User.query.filter_by(Username=form_username).first() is not None
        e_exists = User.query.filter_by(Email=form_email).first() is not None

        if e_exists:
            flash("That email already exists")
            return redirect(url_for('user.register'))

        if u_exists:
            flash("That username already exists")
            return redirect(url_for('user.register'))

        user = User(
            ProfilePic = form.profile.data,
            Email = form_email,
            Username = form_username,
            Password = bcrypt.generate_password_hash(form_pwd).decode('utf-8'),
            IsValidated = False
        )

        db.session.add(user)
        db.session.commit()

        login_user(user, remember = True)
        flash("You are now logged in!")
        return redirect(url_for('main.index'))

    return render_template("user/register.html", form = form)

@userbp.route('/login', methods=['GET','POST'])
def login():

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
            return redirect(url_for('user.login'))
    
    return render_template('user/login.html', form = form)

@userbp.route('/user/logout')
@login_required
def logout():
    logout_user()
    flash("You are now logged out")
    return redirect(url_for('main.index'))

@userbp.route('/account', methods=['GET', 'POST'])
@login_required
def account():    

    user_id = None
    deleteType = None

    if request.method == 'POST':
        req = request.get_json()        
        
        for key in req:
            if key != 'GroupID' and key != 'EventID':
                user_id = int(key)
            else:
                deleteType = key
        
        if user_id == current_user.ID and req[str(user_id)] == current_user.Username:
            if deleteType == 'GroupID':
                group = HangOutGroup.query.filter_by( ID = int(req[deleteType]) ).first()
                db.session.delete(group)

            elif deleteType == 'EventID':
                event = Event.query.filter_by( ID = int(req[deleteType]) ).first()
                db.session.delete(event)

            db.session.commit()

        else:
            print("You are not authenticated")

    profilePic = url_for('static', filename = f"Profiles/{current_user.ProfilePic}.png")

    return render_template("user/account.html", profilePic = profilePic)

@userbp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = editUser(current_user)
    profilePic = url_for('static', filename = f"Profiles/{current_user.ProfilePic}.png")

    if form.validate_on_submit():
        
        user = User.query.filter_by(ID = current_user.ID).first()

        user.ProfilePic = form.profile.data
        
        if form.password.data is None:
            user.Password = form.password.data

        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user.account'))

    return render_template('user/edit.html', form = form, profilePic = profilePic)