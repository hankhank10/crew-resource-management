from flask_login import UserMixin
from . import db
from datetime import datetime, timedelta


class User(UserMixin, db.Model):
    #basics
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    #name details
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))

    @property
    def real_name(self):
        first_name_to_print = self.first_name
        last_name_to_print = self.last_name
        if first_name_to_print == None: first_name_to_print = ""
        if last_name_to_print == None: last_name_to_print = ""
        return first_name_to_print + " " + last_name_to_print

    #dates
    last_login = db.Column(db.DateTime)
    last_action = db.Column(db.DateTime)
    join_date = db.Column(db.DateTime)

    #setup strings
    approved = db.Column(db.Boolean)
    setup = db.Column(db.Boolean)
    unique_setup_key = db.Column(db.String(30))