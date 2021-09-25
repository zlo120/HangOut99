from flask import request, render_template, redirect, Blueprint
from flask_login import login_required, current_user
from .models import User, Event, HangOutGroup
from .form import CreateEvent
from .utils import createDateTimeObject

# Event class
class Event:
    def __init__(self, title, description, time):
        self.title = title
        self.description = description 
        self.time = time
        self.comments = list()

    def __repr__(self):
        return f"Title: {self.title}, Description: {self.description}, Time: {self.time}"

    def addComment(self, comment):
        self.comments.append(comment)

# Event blueprint
eventbp = Blueprint('event', __name__, url_prefix='/event')

# Create event
@eventbp.route('/create', methods = ['GET', 'POST'])
@login_required
def create_event():
    user = User.query.filter_by(Email= current_user.Email ).first()
    form = CreateEvent()
    
    if form.validate_on_submit():
        # Creating a datetime object from the date + time forms
        datetime = createDateTimeObject( request.form['date'] + ' ' + request.form['time'] )
        
        pass

    # if request.method == "POST":
    #     datetime = request.values.get("datetime")
    #     time_obj = createDateTimeObject(datetime)

    return render_template('create.html', form = form, type="event")