from flask import request, render_template, redirect, Blueprint, flash, url_for, Response
from flask_login import login_required, current_user
from sqlalchemy import exc
from sqlalchemy.engine import url

from .models import User, Event, HangOutGroup
from .form import CreateGroup, JoinGroup, editGroup
from .utils import randomString

from . import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(user_id)
    except:
        return None

hangoutbp = Blueprint("hangout", __name__, url_prefix="/hangout")

@hangoutbp.route("/create", methods = ['GET', 'POST'])
def create():
    form = CreateGroup()
    try:
        if form.validate_on_submit():

            group = HangOutGroup(
                Name = form.name.data,
                Creator_ID = current_user.get_id(),
                JoinLink = form.name.data + randomString(10),
                Pin = form.pin.data
            )

            this_user = load_user(current_user.get_id())

            group.Users.append(this_user)

            db.session.add(group)
            db.session.commit()
            
            flash(f"You have created a group called {form.name.data}!")
            return redirect(url_for('main.index', id=group.ID))
    
    except exc.IntegrityError:
        flash(f"That group name already exists")
        return redirect(url_for('hangout.create_hangout'))

    return render_template("group/create.html", form=form, type="hangoutgroup")

@hangoutbp.route("/delete", methods = ['POST'])
def delete():
    user_id = None
    if request.method == 'POST':
        req = request.get_json()  

        for key in req:
            if key != 'GroupID':
                user_id = key

        # group = HangOutGroup.query.filter_by(Name = req['GroupID']).first() 

        # db.session.delete(group)
        # db.session.commit()

        group_name = req['GroupID']

        db.engine.execute(f'DELETE FROM hangoutgroups WHERE "hangoutgroups.Name" = \'{ group_name }\';')

    return Response("Got it", status=201, mimetype='application/json')

@hangoutbp.route("/view/<int:id>")
def view(id):

    # Check if user is in the group first
    group = HangOutGroup.query.filter_by(ID = id).first()
    if group is None or group not in current_user.hangoutgroup:
        return redirect(url_for('event.explore'))

    return render_template("group/view.html", group = group)

@hangoutbp.route("/join", methods = ['POST', 'GET'])
def join():

    form = JoinGroup()

    if form.validate_on_submit():        
        group = HangOutGroup.query.filter_by(Name = form.name.data).first()

        if group :
            
            if group in current_user.hangoutgroup:
                
                return redirect(url_for('main.index'))
            else:
                
                # Check pin
                if form.pin.data == group.Pin:
                    group.Users.append(current_user)
                    db.session.add(group)
                    db.session.commit()
                    return redirect(url_for('main.index'))
                    
                else:
                    return redirect(url_for('hangout.join'))      

        else:
            # Doesn't exist
            return redirect(url_for('hangout.join'))

    return render_template("group/join.html", form = form)

@hangoutbp.route("/link/<string:id>")
@login_required
def link(id):
    group = HangOutGroup.query.filter_by(JoinLink = id).first()

    if group is None:
        print("This group doesn't exist")
        return redirect(url_for('event.explore'))

    if group in current_user.hangoutgroup:
        print("You're already in this group!")
    else:
        print("You're not in this group yet...")
        return redirect(url_for('hangout.view', id = group.ID))

    return redirect(url_for('hangout.view', id = group.ID))
    
@hangoutbp.route("/explore")
def explore():

    return render_template("hangout.html", type="explore")

@hangoutbp.route('/edit/<int:id>', methods = ['POST', 'GET'])
def edit(id):
    group = HangOutGroup.query.filter_by(ID = id).first()

    form = editGroup(group)

    if form.validate_on_submit():
        try:
            group.Name = form.name.data
            
            if form.pin.data:
                group.Pin = form.pin.data
            
            db.session.add(group)
            db.session.commit()

            return redirect(url_for('user.account', id = current_user.ID))

        except exc.IntegrityError:
            flash("A group with that name already exists!")
            return redirect(url_for('hangout.edit', id = id))

    return render_template("group/edit.html", form = form, group = group)