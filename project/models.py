from flask_login import UserMixin
from . import db
from datetime import datetime, timedelta


class User(UserMixin, db.Model):
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


class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    unique_reference = db.Column(db.String(20))

    source = db.Column(db.String(20))
    source_ident = db.Column(db.String(100))

    title = db.Column(db.String(100))
    atc_id = db.Column(db.String(30))

    daparture_code = db.Column(db.String(10))
    departure_name = db.Column(db.String(50))
    departure_scheduled_time = db.Column(db.DateTime)

    arrival_code = db.Column(db.String(10))
    arrival_name = db.Column(db.String(10))
    departure_arrival_time = db.Column(db.DateTime)

    expected_duration = db.Column(db.Integer)


class FlightEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)

    event_time = db.Column(db.DateTime)

    event_type = db.Column(db.String(50))  # "location_update" or "other"

    # if event_type = location_update
    current_latitude = db.Column(db.Float)
    current_longitude = db.Column(db.Float)

    # if event_type != location_update
    event_initiated_by = db.Column(db.String(20))  # pilot, simulator, crew, passenger
    event_name = db.Column(db.String(100))
    event_description = db.Column(db.String(500))


class EquipmentType(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    manufacturer = db.Column(db.String(30))  # eg Boeing
    model = db.Column(db.String(20))  # 747-800

    operator = db.Column(db.String(100))  # British Airways

    first_class_seats = db.Column(db.Integer)
    business_class_seats = db.Column(db.Integer)
    premium_seats = db.Column(db.Integer)
    economy_seats = db.Column(db.Integer)

    maximum_cabin_crew = db.Column(db.Integer)

    approved_for_general_use = db.Column(db.Boolean)
    created_by_user = db.Column(db.Integer)

