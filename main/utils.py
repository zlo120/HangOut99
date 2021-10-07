from datetime import datetime
import os, string, random, smtplib, ssl, csv

from .models import User

from . import db
from . import login_manager

@login_manager.user_loader
def user_loader(id):
    return User.query.get(id)

# Printing sql
# ('ZacL', 'The bois')

# Group related functions
def getHangOutID(user, group):
    groups = user.hangoutgroup
    ans = None

    for curr_group in groups:
        if group == curr_group:
            ans = curr_group
            break

    if ans is not None:
        return group.ID
    else:
        return None

def getGroupByEvent(event):
    res = db.engine.execute(f"SELECT Name FROM hangoutgroups WHERE ID = {event.ID};")
    for row in res:
        return row[0]

# Other utils
# create a datetime object
def createDateTimeObject(time):

    year = time[:4]
    month = time[5:7]
    day = time[8:10]

    time = time[11:]

    try:
        if time == 'None':
            date_time = f"{day}/{month}/{year[2:]} 00:00"
            return datetime.strptime(date_time, '%d/%m/%y %H:%M')

        date_time = f"{day}/{month}/{year[2:]} " + time
        
        return datetime.strptime(date_time , '%d/%m/%y %H:%M:%S')

    except:
        return None

def randomString(num):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(num))

# send email
def send_email(TOKEN, receiver, validationForm = True):
    port = 465  # For SSL
    password = "Wasd123!"
    sender_email = "GamerIO5500@gmail.com"
    if validationForm:
        message = f"""\
        Validate Email

        This message is sent from GamerIO.
        
        Your code is: {TOKEN}

        You can authenticate your code here: http://124.176.55.35:5500/user/authenticate/
        
        This email is generated by GamerIO, made by Zachary Lo. Don't worry I'm not gonna give you virus.
        """

    else:
        message = f"""\
        Test Email

        Let's see if this link will work
        
        You can authenticate your code here: http://124.176.55.35:5500/user/user-id/{TOKEN}
        
        This email is generated by GamerIO, made by Zachary Lo. Don't worry I'm not gonna give you virus.
        """

    # Create a secure SSL context
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("GamerIO5500@gmail.com", password)
        server.sendmail(sender_email, receiver, message)