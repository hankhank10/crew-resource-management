from flask_login import UserMixin
from . import db
from datetime import datetime, timedelta
from project import equipment
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method



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
    def passengers_total(self):
        return self.passengers_first_class + self.passengers_business_class + self.passengers_premium_class + self.passengers_economy_class

    @property
    def operator_logo(self):
        return equipment.lookup_logo(self.equipment_operator, "operator")

    @property
    def manufacturer_logo(self):
        return equipment.lookup_logo(self.equipment_manufacturer, "manufacturer")

    @property
    def phase_flight_name(self):
        phase = FlightPhase.query.filter_by(id = self.phase_flight).first()
        if phase is None: return None
        return phase.phase_name

    @property
    def phase_cabin_name(self):
        phase = FlightPhase.query.filter_by(id=self.phase_cabin).first()
        if phase is None: return None
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
        # FLIGHT
        # At Gate
        # Taxi for Takeoff
        # Takeoff and Climb
        # Cruise
        # Descent and landing
        # Taxi to gate
        # Shutdown

        # CABIN
        # Pre-Boarding
        # Boarding
        # Cabin Secure
        # Drinks Service
        # Meal Service


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


class Seat(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    flight = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=True)

    seat_number = db.Column(db.String(4))

    manifest_number = db.Column(db.Integer)

    y = db.Column(db.Integer)  # Row number
    x = db.Column(db.Integer)  # Column number

    seat_type = db.Column(db.String(1))  # F=First, B=Business, P=Premium, E=Economy, X=Blank, " "=Blank

    @property
    def seat_type_text(self):
        if self.seat_type is None: return None
        if self.seat_type == "F": return "First"
        if self.seat_type == "B": return "Business"
        if self.seat_type == "P": return "Premium"
        if self.seat_type == "E": return "Economy"
        if self.seat_type == "X": return ""
        if self.seat_tyoe == " ": return ""

    occupied = db.Column(db.Boolean())
    occupied_by = db.Column(db.Integer)

    phase = db.Column(db.String(25), default="Pre Flight")

    activity = db.Column(db.String(50))

    is_seated = db.Column(db.Boolean, default=False)

    status_bladder_need = db.Column(db.Integer)
    status_hunger = db.Column(db.Integer)
    status_thirst = db.Column(db.Integer)

    # Times things happen at
    time_start_boarding = db.Column(db.DateTime)
    time_seated = db.Column(db.DateTime)

    @property
    def status(self):
        waiting_to_board = "Waiting to Board"
        boarding = "Boarding"
        boarded = "Boarded"
        deboarding = "Deboarding"
        deboarded = "Deboarded"

        if self.time_start_boarding == None: return waiting_to_board
        if self.time_start_boarding <= datetime.utcnow(): return waiting_to_board

        if self.phase == "Pre Flight":

            if self.time_seated == None: return boarding
            if self.time_seated <= datetime.utcnow(): return boarding

            if self.time_seated >= datetime.utcnow(): return boarded


    @property
    def full_name(self):
        if self.occupied_by is None: return None
        passenger = Passenger.query.filter_by(id=self.occupied_by).first()
        return passenger.full_name

    @property
    def frequent_flyer_status(self):
        if self.occupied_by is None: return None
        passenger = Passenger.query.filter_by(id=self.occupied_by).first()
        return passenger.frequent_flyer_status

    @property
    def frequent_flyer_status_text(self):

        if self.frequent_flyer_status == 0: return "None"
        if self.frequent_flyer_status == 1: return "Blue"
        if self.frequent_flyer_status == 2: return "Bronze"
        if self.frequent_flyer_status == 3: return "Silver"
        if self.frequent_flyer_status == 4: return "Gold"
        if self.frequent_flyer_status == 5: return "VIP"


class Passenger(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    second_name = db.Column(db.String(50))

    @property
    def full_name(self):
        return self.first_name + " " + self.second_name

    age = db.Column(db.Integer)
    frequent_flyer_status = db.Column(db.Integer)