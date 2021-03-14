from flask_login import UserMixin
from . import db
from datetime import datetime, timedelta
from project import equipment


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

    active_flight_id = db.Column(db.Integer, default=None)

    unread_flight_messages = db.Column(db.Integer, default=0)

    @property
    def active_flight_unique_reference(self):
        if self.active_flight_id == None:
            return None

        active_flight = Flight.query.filter_by(id=self.active_flight_id).first()
        return active_flight.unique_reference


class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    unique_reference = db.Column(db.String(20))

    source = db.Column(db.String(20))
    source_ident = db.Column(db.String(100))

    title = db.Column(db.String(100))
    atc_id = db.Column(db.String(30))

    departure_code = db.Column(db.String(10))
    departure_name = db.Column(db.String(50))
    departure_scheduled_time = db.Column(db.DateTime)

    equipment_full_name = db.Column(db.String(100))
    equipment_manufacturer = db.Column(db.String(50))
    equipment_operator = db.Column(db.String(50))
    equipment_model = db.Column(db.String(50))

    destination_code = db.Column(db.String(10))
    destination_name = db.Column(db.String(10))
    departure_arrival_time = db.Column(db.DateTime)

    passengers_first_class = db.Column(db.Integer)
    passengers_business_class = db.Column(db.Integer)
    passengers_premium_class = db.Column(db.Integer)
    passengers_economy_class = db.Column(db.Integer)

    cabin_crew_count = db.Column(db.Integer)

    expected_duration_minutes = db.Column(db.Integer)

    started = db.Column(db.Boolean, default=False)
    completed = db.Column(db.Boolean, default=False)

    phase_flight = db.Column(db.Integer)
    phase_cabin = db.Column(db.Integer)
    phase_seatbelt_sign = db.Column(db.Integer)

    # Current flight variables
    current_altitude = db.Column(db.Integer)
    current_speed = db.Column(db.Integer)
    on_ground = db.Column(db.Boolean)
    seatbelt_sign = db.Column(db.Boolean)
    no_smoking_sign = db.Column(db.Boolean)
    door_status = db.Column(db.Integer)
    parking_brake = db.Column(db.Boolean)
    gear_handle_position = db.Column(db.Integer)

    @property
    def seatbelt_sign_text(self):
        if self.seatbelt_sign == None: return ["Unknown", "yellow"]
        if self.seatbelt_sign == True: return ["On", "green"]
        if self.seatbelt_sign == False: return ["Off", "red"]

    @property
    def no_smoking_sign_text(self):
        if self.no_smoking_sign == None: return ["Unknown", "yellow"]
        if self.no_smoking_sign == True: return ["On", "green"]
        if self.no_smoking_sign == False: return ["Off", "red"]

    @property
    def door_status_text(self):
        if self.door_status == None: return ["Unknown", "yellow"]
        if self.door_status == 0: return ["Secured", "green"]
        if self.door_status == 1: return ["Open", "red"]

    @property
    def passengers_total(self):
        return self.passengers_first_class + self.passengers_business_class + self.passengers_premium_class + self.passengers_economy_class

    @property
    def operator_logo(self):
        return equipment.lookup_logo(self.equipment_operator, "operator")

    @property
    def manufacturer_logo(self):
        return equipment.lookup_logo(self.equipment_manufacturer, "manufacturer")

    @property
    def phase_name(self, phase_category="flight"):
        phase = FlightPhase.query.filter_by(flight = self.id, phase_category=phase_category).first()

        if phase is None:
            return None

        return phase.phase_name


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
    event_code = db.Column(db.String(50))
    event_name = db.Column(db.String(100))
    event_description = db.Column(db.String(500))
    event_additional_detail = db.Column(db.String(500))
    associated_message = db.Column(db.Integer)

    read = db.Column(db.Boolean, default=False)


class FlightMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)

    message_time = db.Column(db.DateTime)

    message_type = db.Column(db.String(10))  # cabin, crew
    message_from = db.Column(db.String(10))  # pilot, crew
    message_to = db.Column(db.String(10))  # pilot, crew, cabin
    message_content = db.Column(db.String(500))

    read = db.Column(db.Boolean, default=False)

    @property
    def seconds_since_epoch(self):
        return self.message_time.timestamp()


class FlightPhase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)

    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    is_current = db.Column(db.Boolean)

    phase_category = db.Column(db.String(20))
        # flight
        # cabin
        # seatbelt_sign

    phase_name = db.Column(db.String(50))
        # Pre-Boarding
        # Boarding
        # Securing cabin
        # Taxi for takeoff
        # Takeoff
        # Climb
        # Cruise
        # Descent and landing
        # Taxi to gate
        # Deboarding


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

