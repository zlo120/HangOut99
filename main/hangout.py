from flask import request, render_template, redirect, Blueprint, flash, url_for
from flask_login import login_required, current_user
from sqlalchemy import exc
from .models import User, Event, HangOutGroup
from .form import CreateGroup

from . import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(user_id)
    except:
        return None

hangoutbp = Blueprint("hangout", __name__, url_prefix="/hangout")

@hangoutbp.route("/create", methods = ['GET', 'POST'])
def create_hangout():
    form = CreateGroup()
    try:
        if form.validate_on_submit():

            group = HangOutGroup(
                Name = form.name.data
            )      

            this_user = load_user(current_user.get_id())

            # If this_user.Groups has has stuff in it
            if (this_user.Groups):
                groups = this_user.Groups
                this_user.Groups = groups + f",{form.name.data}"
                
            # If there isn't anything in this_user.Groups
            else:
                this_user.Groups = form.name.data

            group.Users.append(this_user)

            db.session.add(group)
            db.session.commit()
            
            flash(f"You have created a group called {form.name.data}!")
            return redirect(url_for('main.index'))
    
    except exc.IntegrityError:
        flash(f"That group name already exists")
        return redirect(url_for('hangout.create_hangout'))

    return render_template("create.html", form=form, type="hangoutgroup")