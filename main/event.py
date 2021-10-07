from flask import request, render_template, redirect, Blueprint, flash, Response
from flask.helpers import url_for
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from .routes import load_user
from .models import HangOutGroup, User, Event, Comment, Photo
from .form import createEventForm, createEditForm, CreateComment, UploadImage
from .utils import createDateTimeObject, getGroupByEvent, getHangOutID, getUserGroups, user_loader
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

        print("Added")

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

        print("Added")

    return Response("Got it", status=201, mimetype='application/json')

@eventbp.route('/explore')
def explore():

    if current_user.is_authenticated:
        this_user = User.query.filter_by(Email = current_user.Email).first()

        temp = getUserGroups(this_user.ID)
        groups = []
        events = []

        for row in temp:
            hangout = HangOutGroup.query.filter_by(Name = row[1]).first()
            groups.append(hangout)

        for group in groups:
            events.append(group.Events)

        available_event_ids = []
        unavailable_event_ids = []

        for event in this_user.event:
            available_event_ids.append(event.ID)

        for event in this_user.unavailableEvent:
            unavailable_event_ids.append(event.ID)  

        return render_template('explore.html', events = events, user = this_user, available_event_ids = available_event_ids, unavailable_event_ids = unavailable_event_ids)

    return render_template('explore.html')

# Create event
@eventbp.route('/create', methods = ['GET', 'POST'])
@login_required
def create_event():

    # Get the groups the user is in
    temp = getUserGroups(current_user.get_id())
    groups = []

    for row in temp:
        group = HangOutGroup.query.filter_by(Name = row[1]).first()
        groups.append(group)

    if groups == []:
        flash("You need to be in a group before making an event!")
        return redirect(url_for('main.index'))

    user = User.query.filter_by( Email= current_user.Email ).first()
    form = createEventForm(user)
    
    if form.validate_on_submit():

        # Creating a datetime object from the date + time forms
        datetime = createDateTimeObject( str(form.date.data) + ' ' + str(form.time.data) )

        if form.location.data:
            location = form.location.data
            link = f"https://maps.google.com/?q={form.location.data}"
        else:
            location = None
            link = None

        event = Event(
            Creator_ID = user.ID,
            Name = form.title.data,
            Description = form.description.data,
            DateTime = datetime,
            Hangout_ID = getHangOutID(user, form.group.data),
            Location = location,
            Link = link
        )

        event.Users.append(user)

        db.session.add(event)
        db.session.commit()

        flash("You have created your event!")
        return redirect(url_for('main.index'))

    return render_template('create.html', form = form, type="event")

@eventbp.route('/view/<id>', methods=['GET', 'POST'])
@login_required
def event(id):

    exists = False
    # Check if event exists
    res = db.engine.execute(f"SELECT ID FROM events WHERE ID = {id}")
    results = []
    for row in res:
        results.append(res)

    if results == []:
        return render_template("event.html", exists = exists)

    exists = True

    # Check to make sure the user is in the correct group for this event
    this_user = load_user(current_user.get_id())

    isEligible = False

    # Get the groups the user is in
    temp = getUserGroups(this_user.ID)
    groups = []

    for row in temp:
        group = HangOutGroup.query.filter_by(Name = row[1]).first()
        groups.append(group)
        
    # Get the group this event is for
    this_event = Event.query.filter_by(ID = id).first()

    # this_group = getGroupByEvent(this_event)
    this_group = this_event.hangoutgroup

    if this_group in groups:
        isEligible = True
    
    base_url = request.base_url
    temp = base_url.index("event")
    url = base_url[0:temp - 1]

    form = CreateComment()

    if form.validate_on_submit():

        comment = Comment(
            Creator_ID = current_user.Username,
            Content = form.comment.data,
            Event_ID = this_event.ID
        )

        db.session.add(comment)
        db.session.commit()

        return redirect(url_for('event.event', id=this_event.ID))

    image_form = UploadImage()

    if image_form.validate_on_submit():

        if image_form.image.data is None:
            flash("You need to upload an image!")
            return redirect(url_for('event.event', id = id))

        db_file_path = check_upload_file(image_form)

        photo = Photo(
            Image = db_file_path,
            Creator_ID = current_user.ID,
            Event_ID = id
        )    

        db.session.add(photo)
        db.session.commit()

    return render_template("event.html", Eligible = isEligible, event = this_event, exists = exists, url = url, form = form, image_form = image_form)

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

        print("deleted")
            
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
        
        date_time = createDateTimeObject( str(form.date.data) + ' ' + str(form.time.data) )

        if date_time:
            this_event.DateTime = date_time

        db.session.add(this_event)
        db.session.commit()

        flash("You have updated the event!")
        return redirect(url_for('event.event', id = id))
    
    return render_template("update.html", event = this_event, form = form)



