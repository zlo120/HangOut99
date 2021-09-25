from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = None
db = SQLAlchemy()
bcrypt = None
login_manager = LoginManager()

def initialize_db():
    global app
    global db
    global bcrypt
    global login_manager

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

    db = SQLAlchemy(app)

    return app, db

def create_app():
    global app
    global db
    global bcrypt
    global login_manager

    app = Flask(__name__)
    app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    db.init_app(app)
    bcrypt = Bcrypt(app)
    login_manager.init_app(app)

    from . import user, event, routes, hangout

    app.register_blueprint(user.userbp)
    app.register_blueprint(event.eventbp)
    app.register_blueprint(routes.mainbp)
    app.register_blueprint(hangout.hangoutbp)

    return app