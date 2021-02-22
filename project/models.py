from flask_login import UserMixin
from . import db
from datetime import datetime, timedelta


class User(UserMixin, db.Model):
    #basics
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    #username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    name = db.Column(db.String(100))

    #dates
    last_login = db.Column(db.DateTime)
    last_action = db.Column(db.DateTime)
    join_date = db.Column(db.DateTime)

    #setup strings
    approved = db.Column(db.Boolean)
    unique_setup_key = db.Column(db.String(30))