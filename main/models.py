from . import db

class User(db.Model):
    Email = db.Column(db.String(256), primary_key = True, nullable = False)
    Username = db.Column(db.String(256), nullable = False)
    Password = db.Column(db.String(256), nullable = False)
    IsValidated = db.Column(db.Boolean, nullable = False)
	
    def __repr__(self):
        return f"(Email: {self.Email}, Name: {self.Username}, IsValidated: {self.IsValidated}) "

    def get(self, id):
        return 

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.Email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.IsValidated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

class Tokens(db.Model):
    Email = db.Column(db.String(256), primary_key = True, nullable = False)
    UserToken = db.Column(db.String(256))

    def __repr__(self):
        return f"(Email: {self.Email}, UserToken: {self.Token}) "

class Events(db.Model):
    Email = db.Column(db.String(256), primary_key = True, nullable = False)
    Name = db.Column(db.String(256), nullable = False)
    Description = db.Column(db.String(256), nullable = False)
    DateTime = db.Column(db.DateTime, nullable = False)

    def __repr__(self):
        return f"(Creator's Email: {self.Email}, Title: {self.Name}, Description: {self.Description}, Date and Time: {self.DateTime}) "