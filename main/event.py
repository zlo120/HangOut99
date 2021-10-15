from flask import request, render_template, redirect, Blueprint, flash, Response
from flask.helpers import url_for
from flask_login import login_required, current_user
from datetime import datetime
from flask_login.utils import confirm_login
from sqlalchemy.engine import url
from werkzeug.utils import secure_filename
import os
from .routes import load_user
from .models import HangOutGroup, User, Event, Comment, Photo
from .form import createEventForm, createEditForm, CreateComment, UploadImage
from .utils import createDateTimeObject, user_loader
from . import db

def check_upload_file(form):
  #get file data from form  
  fp=form.image.data
  filename=fp.filename
  #get the current path of the module file… store image file relative to this path  
  BASE_PATH=os.path.dirname(__file__)
  #upload file location – directory of this file/static/image
  upload_path=os.path.join(BASE_PATH,'static/image',secure_filename(filename))
  #store relative path in DB as image location in HTML is relative
  db_upload_path='/static/image/' + secure_filename(filename)
  #save the file and return the db upload path  
  fp.save(upload_path)
  return db_upload_path

# Event blueprint
eventbp = Blueprint('event', __name__, url_prefix='/event')

# JSON request format
#   { user.ID : { event.ID : 'interested' }}
#   {'1': {'3': 'Unavailable'}}

@eventbp.route('/interested', methods = ['POST'])
@login_required
def interested():
    if request.method == "POST":
        res = request.get_json()
        
        # Instance of User class
        this_user = None

        # Dictionary containing the Event key
        event = None

        # Instance of Event class
        this_event = None

        ### Get User
        for key in res:
            this_user = User.query.filter_by(ID = key).first()
        
        ### Get Event
        for key in res:
            event = dict(res[key])

        for key in event:
            this_event = Event.query.filter_by(ID = key).first()

        ### Set user as interested for event
        this_event.Users.append(this_user)

        db.session.add(this_event)

        ### Check if user is in unavailable table
        res = db.engine.execute(f'SELECT user_id FROM unavailable_events WHERE user_id = {this_user.ID} AND event_id = {this_event.ID};')

        results = [row[0] for row in res]
        
        # This is user.ID
        try:
            res = results[0]
            db.engine.execute(f"DELETE FROM unavailable_events WHERE user_id = {res} and event_id = {this_event.ID};")

        except IndexError:
            pass

        db.session.commit()

    return Response("Got it", status=201, mimetype='application/json')

@eventbp.route('/unavailable', methods = ['POST'])
@login_required
def unavailable():
    if request.method == "POST":
        res = request.get_json()
        # Instance of User class
        this_user = None

        # Dictionary containing the Event key
        event = None

        # Instance of Event class
        this_event = None

        ### Get User
        for key in res:
            this_user = User.query.filter_by(ID = key).first()
        
        ### Get Event
        for key in res:
            event = dict(res[key])

        for key in event:
            this_event = Event.query.filter_by(ID = key).first()

        ### Set user as unavailable for event
        this_event.UnavailableUsers.append(this_user)

        db.session.add(this_event)

        ### Check if user is in interested table
        res = db.engine.execute(f'SELECT user_id FROM interested_events WHERE user_id = {this_user.ID} AND event_id = {this_event.ID};')

        results = [row[0] for row in res]
        
        # This is user.ID
        try:
            res = results[0]

            db.engine.execute(f"DELETE FROM interested_events WHERE user_id = {res} and event_id = {this_event.ID};")

        except IndexError:
            pass

        db.session.commit()

    return Response("Got it", status=201, mimetype='application/json')

@eventbp.route('/explore')
@login_required
def explore():

    event_dates = []
    for event in current_user.event:
        if event.DateTime is None:
            continue
        
        event_dates.append( event.DateTime )  

    latest_event = None

    print(event_dates)

    try:
        latest_date = min(event_dates)
        latest_event = Event.query.filter_by(DateTime = latest_date).first()

    except:
        pass
 
    
    return render_template('feed.html', latest_event = latest_event)

# Create event
@eventbp.route('/create', methods = ['GET', 'POST'])
@login_required
def create():
    if current_user.hangoutgroup == []:
        flash("You need to be in a group before making an event!")
        return redirect(url_for('main.index'))

    event_form = createEventForm(current_user)
    
    if event_form.validate_on_submit():

        print("\n\nValidated\n\n")

        # Creating a datetime object from the date + time forms
        datetime = createDateTimeObject( str(event_form.date.data) + ' ' + str(event_form.time.data) )

        if event_form.location.data:
            location = event_form.location.data
            link = f"https://maps.google.com/?q={event_form.location.data}"
        else:
            location = None
            link = None

        group = HangOutGroup.query.filter_by(Name = event_form.group.data).first()

        event = Event(
            Creator_ID = current_user.ID,
            Name = event_form.title.data,
            Description = event_form.description.data,
            DateTime = datetime,
            Hangout_ID = group.ID,
            Location = location,
            Link = link
        )

        event.Users.append(current_user)

        db.session.add(event)
        db.session.commit()

        flash("You have created your event!")
        return redirect(url_for('main.index'))

    return render_template('event/create.html', form = event_form)

@eventbp.route('/view/<id>', methods=['GET', 'POST'])
@login_required
def event(id):    

    return render_template("event/view.html", event = Event.query.filter_by(ID = id).first())

@eventbp.route('/delete', methods = ['POST'])
def delete():
    if request.method == 'POST':
        res = request.get_json()
        event_id = None
        for key in res:
            event_id = res[key]

        if event_id:  
            db.engine.execute(f"DELETE FROM events WHERE ID = {event_id};")
            db.engine.execute(f"DELETE FROM interested_events WHERE user_id = {current_user.get_id()} and event_id = {event_id};")  
            db.engine.execute(f"DELETE FROM unavailable_events WHERE user_id = {current_user.get_id()} and event_id = {event_id};")  
            
    return Response("Got it", status=201, mimetype='application/json')

@eventbp.route('/edit/<int:id>', methods = ['GET', 'POST'])
def edit(id):

    this_event = Event.query.filter_by(ID = id).first()

    form = createEditForm(current_user, this_event)

    if this_event is None:
        return redirect(url_for('main.index'))

    if form.validate_on_submit():        
        
        this_event.Name = form.title.data
        this_event.Description = form.description.data
        
        if form.location.data:
            this_event.Location = form.location.data
            this_event.Link = f"https://maps.google.com/?q={form.location.data}"
        
        date_time = createDateTimeObject( str(form.date.data) + ' ' + str(form.time.data) )

        if date_time:
            this_event.DateTime = date_time

        db.session.add(this_event)
        db.session.commit()

        flash("You have updated the event!")
        return redirect(url_for('main.index'))
    
    return render_template("event/edit.html", event = this_event, form = form)



