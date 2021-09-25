from enum import unique
from sqlalchemy.sql.schema import ForeignKey
from . import db

# Association table
user_identifier = db.Table(
    'user_identifier',
    db.Column('hangoutgroup_id', db.Integer, db.ForeignKey('hangoutgroups.ID')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.ID'))
)


class User(db.Model):
    __tablename__ = "users"
    ID = db.Column(db.Integer, primary_key = True, nullable = False, autoincrement=True)
    Email = db.Column(db.String(256), nullable = False)
    Username = db.Column(db.String(256), nullable = False)
    Password = db.Column(db.String(256), nullable = False)
    IsValidated = db.Column(db.Boolean, nullable = False)
    Groups = db.Column(db.String(256))
	
    def __repr__(self):
        return f"(Email: {self.Email}, Name: {self.Username}, IsValidated: {self.IsValidated}) "

    def get(self, id):
        return self.ID

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.ID

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

class Token(db.Model):
    __tablename__ = "tokens"
    Email = db.Column(db.String(256), primary_key = True, nullable = False)
    UserToken = db.Column(db.String(256))

    def __repr__(self):
        return f"(Email: {self.Email}, UserToken: {self.Token}) "


class HangOutGroup(db.Model):
    __tablename__ = "hangoutgroups"
    ID = db.Column(db.Integer, primary_key = True, nullable = False, autoincrement=True)
    Name = db.Column(db.String(256), nullable = False, unique = True)

    Users = db.relationship("User", secondary=user_identifier, backref="hangoutgroup")

    Events = db.relationship('Event', backref='hangoutgroup')
    
    def __repr__(self):
        return f"This is the {self.Name} group, the users are: {self.Users}. "
    
class Event(db.Model):
    __tablename__ = "events"
    ID = db.Column(db.Integer, primary_key = True, nullable = False, autoincrement=True)
    Email = db.Column(db.String(256), nullable = False)
    Name = db.Column(db.String(256), nullable = False)
    Description = db.Column(db.String(256), nullable = False)
    DateTime = db.Column(db.DateTime, nullable = False)
    
    Hangout_ID = db.Column(db.Integer, db.ForeignKey('hangoutgroups.ID'))

    def __repr__(self):
        return f"This event is called {self.Name}, for {self.hangoutgroup.Name}"