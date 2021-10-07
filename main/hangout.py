from flask import request, render_template, redirect, Blueprint, flash, url_for, Response
from flask_login import login_required, current_user
from sqlalchemy import exc
from sqlalchemy.engine import url

from .models import User, Event, HangOutGroup
from .form import CreateGroup, JoinGroup, EditGroup
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
def create_hangout():
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
            return redirect(url_for('hangout.view', id=group.ID))
    
    except exc.IntegrityError:
        flash(f"That group name already exists")
        return redirect(url_for('hangout.create_hangout'))

    return render_template("create.html", form=form, type="hangoutgroup")

@hangoutbp.route("/delete", methods = ['POST'])
def delete():

    if request.method == 'POST':
        res = request.get_json()
        this_user = None
        this_group = None
        for key in res:
            this_user = User.query.filter_by(ID = key).first()
            this_group = HangOutGroup.query.filter_by(ID = res[key]).first()

        if this_user and this_group:
            for event in this_group.Events:
                db.engine.execute(f"DELETE FROM interested_events WHERE user_id = {current_user.get_id()} and event_id = {event.ID};")  
                db.engine.execute(f"DELETE FROM unavailable_events WHERE user_id = {current_user.get_id()} and event_id = {event.ID};") 

            db.engine.execute(f"DELETE FROM hangoutgroups WHERE ID = {this_group.ID};")    
            db.engine.execute(f"DELETE FROM events WHERE Hangout_ID = {this_group.ID};") 
            db.engine.execute(f"DELETE FROM user_identifier WHERE user_id = {current_user.get_id()} and hangoutgroup_id = {this_group.ID};")
                           
            
    return Response("Got it", status=201, mimetype='application/json')

@hangoutbp.route("/view/<int:id>")
def view(id):

    base_url = request.base_url
    temp = base_url.index("hangout")
    base_url = base_url[0:temp - 1]

    return render_template("hangout.html", type="view", group = HangOutGroup.query.filter_by(ID = id).first(), base_url = base_url)

@hangoutbp.route("/join", methods = ['POST', 'GET'])
def join():

    form = JoinGroup()

    if form.validate_on_submit():
        
        group = HangOutGroup.query.filter_by(Name = form.name.data).first()
        if group:            
            
            for this_group in current_user.hangoutgroup:
                if this_group == group:
                    flash(f"You are already in the {group.Name} HangOut group!")
                    return redirect(url_for('hangout.join'))

            if group.Pin == form.pin.data:
                db.engine.execute(f"INSERT INTO user_identifier (hangoutgroup_id, user_id) VALUES ({group.ID}, {current_user.get_id()})")
                flash(f"You have joined the {group.Name} HangOut group!")
                return redirect(url_for('hangout.view', id = group.ID))

            else:
                flash("Your group name or pin is incorrect")
                return redirect(url_for('hangout.join'))

        else:
            flash("Your group name or pin is incorrect")
            return redirect(url_for('hangout.join'))

    return render_template("hangout.html", type="join", form = form)

@hangoutbp.route("/link/<string:id>")
@login_required
def link(id):
    group = HangOutGroup.query.filter_by(JoinLink = id).first()

    if group == None:
        flash("That link doesn't work...")
        return redirect(url_for('main.index'))

    for this_group in current_user.hangoutgroup:
        if this_group == group:
            flash(f"You are already in the {group.Name} HangOut group!")
            return redirect(url_for('hangout.view', id = group.ID))

    db.engine.execute(f"INSERT INTO user_identifier (hangoutgroup_id, user_id) VALUES ({group.ID}, {current_user.get_id()})")
    flash(f"You have joined the {group.Name} HangOut group!")
    return redirect(url_for('hangout.view', id = group.ID))
    
@hangoutbp.route("/explore")
def explore():

    return render_template("hangout.html", type="explore")

@hangoutbp.route('/edit/<int:id>', methods = ['POST', 'GET'])
def edit(id):
    group = HangOutGroup.query.filter_by(ID = id).first()

    form = EditGroup()

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

    return render_template("hangout.html", type="edit", form = form)