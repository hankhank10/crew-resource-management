from flask_login import UserMixin
from . import db
from datetime import datetime, timedelta
from project import equipment_logos
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
    is_active = db.Column(db.Boolean)

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

    seatmap_text = db.Column(db.String(5000))
    number_of_seats_across = db.Column(db.Integer)
    number_of_rows = db.Column(db.Integer)

    last_event_recorded = db.Column(db.DateTime, default=datetime.utcnow())
    number_of_updates_received = db.Column(db.Integer, default=0)

    new_event = db.Column(db.String(100))

    @property
    def passengers_total(self):
        return self.passengers_first_class + self.passengers_business_class + self.passengers_premium_class + self.passengers_economy_class

    @property
    def operator_logo(self):
        return equipment_logos.lookup_logo(self.equipment_operator, "operator")

    @property
    def manufacturer_logo(self):
        return equipment_logos.lookup_logo(self.equipment_manufacturer, "manufacturer")

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
    current_altitude = db.Column(db.Integer)

    # if event_type != location_update
    event_initiated_by = db.Column(db.String(20))  # pilot, simulator, crew, passenger
    event_name = db.Column(db.String(100))

    read = db.Column(db.Boolean, default=False)

    @property
    def event_description(self):

        if self.event_type == None: return "error"
        if self.event_type == "location_update": return "Location update"

        if self.event_name == None: return None

        if self.event_name == "start_boarding_passengers": return "Passenger boarding started"
        if self.event_name == "passenger_boarding_complete": return "Passenger boarding complete"

        if self.event_name == "no_smoking_sign_turned_off": return "No smoking sign turned off"
        if self.event_name == "no_smoking_sign_turned_on": return "No smoking sign turned on"
        if self.event_name == "seatbelt_sign_turned_on": return "Seatbelt sign turned on"
        if self.event_name == "seatbelt_sign_turned_off": return "Seatbelt sign turned off"

        if self.event_name == "cabin_door_opened": return "Cabin doors opened"
        if self.event_name == "cabin_door_closed": return "Cabin doors closed"

        if self.event_name == "begin_taxi_for_takeoff": return "Start taxi for takeoff"

        if self.event_name == "cabin_announcement": return "Cabin announcement by pilot"
        if self.event_name == "crew_seats_for_takeoff": return "Crew seats for takeoff"

        if self.event_name == "takeoff": return "Takeoff"

        if self.event_name == "flight_phase_at gate": return "Phase set to at gate"
        if self.event_name == "flight_phase_taxi for takeoff": return "Begin taxi for takeoff phase"
        if self.event_name == "flight_phase_takeoff and climb": return "Begin takeoff phase"
        if self.event_name == "flight_phase_cruise": return "Begin cruise phase"

        return self.event_name



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
    model = db.Column(db.String(30))  # 747-800
    variant = db.Column(db.String(20))
    full_name = db.Column(db.String(100))

    operator = db.Column(db.String(100))  # British Airways

    first_class_seats = db.Column(db.Integer)
    business_class_seats = db.Column(db.Integer)
    premium_class_seats = db.Column(db.Integer)
    economy_class_seats = db.Column(db.Integer)

    maximum_cabin_crew = db.Column(db.Integer)

    approved_for_general_use = db.Column(db.Boolean, default=True)
    created_by_user = db.Column(db.Integer)

    seatmap_text = db.Column(db.String(5000))

    number_of_seats_across = db.Column(db.Integer)
    number_of_rows = db.Column(db.Integer)

    @property
    def operator_logo_url(self):
        return equipment_logos.lookup_logo(self.operator, "operator")

    @property
    def manufacturer_logo_url(self):
        return equipment_logos.lookup_logo(self.manufacturer, "manufacturer")


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

    phase = db.Column(db.String(25))

    activity = db.Column(db.String(50))

    is_seated = db.Column(db.Boolean, default=False)

    status_bladder_need = db.Column(db.Integer)  # Lower is better
    status_hunger = db.Column(db.Integer)   # Lower is better
    status_thirst = db.Column(db.Integer)   # Lower is better

    current_activity = db.Column(db.String)
    current_activity_will_end_at = db.Column(db.DateTime)

    next_increment_due = db.Column(db.DateTime, default = datetime.utcnow())

    @property
    def status_bladder_need_text(self):
        if self.status_bladder_need > 90: return "Desperate for toilet"
        if self.status_bladder_need > 80: return "Desperate for the toilet"
        if self.status_bladder_need > 50: return "Needs the toilet soon"
        return ""

    @property
    def status_hunger_text(self):
        if self.status_hunger > 90: return "Starving"
        if self.status_hunger > 80: return "Very Hungry"
        if self.status_hunger > 50: return "Hungry"
        if self.status_hunger > 40: return "Peckish"
        return ""

    @property
    def status_thirst_text(self):
        if self.status_thirst > 90: return "Parched"
        if self.status_thirst > 80: return "Very Thirsty"
        if self.status_thirst > 50: return "Thirsty"
        return ""


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

        if self.seat_type == " " or self.phase == "Empty seat" or self.phase == None:
            return "Empty seat"

        has_started_boarding = False
        has_sat = False

        if self.phase == "Pre Flight":

            if self.time_start_boarding == None: return waiting_to_board
            if self.time_seated == None: return waiting_to_board

            if self.time_start_boarding < datetime.utcnow():
                has_started_boarding = True

            if self.time_seated < datetime.utcnow():
                self.is_seated = True
                db.session.commit()
                has_sat = True

        if has_sat == True:
            return boarded

        if has_started_boarding == True and has_sat == False:
            return boarding

        if has_started_boarding == False: return waiting_to_board

        return "weird error"



    @property
    def full_name(self):
        if self.occupied_by is None: return None
        passenger = Passenger.query.filter_by(id=self.occupied_by).first()
        return passenger.full_name

    @property
    def gender(self):
        if self.occupied_by is None: return None
        passenger = Passenger.query.filter_by(id=self.occupied_by).first()
        return passenger.gender

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

    gender = db.Column(db.String(6))


class CrewPopulation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    second_name = db.Column(db.String(50))

    @property
    def full_name(self):
        return self.first_name + " " + self.second_name

    seniority = db.Column(db.Integer, default=0)
    gender = db.Column(db.String(6))
    efficiency = db.Column(db.Integer, default=100)

    @property
    def seniority_text(self):
        if self.seniority == 0: "Crew Member"
        if self.seniority == 1: "Senior Crew Member"
        if self.seniority == 2: "Cabin Service Director"


class CrewMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=True)

    identity = db.Column(db.Integer, db.ForeignKey('crew_population.id'))
    energy = db.Column(db.Integer, default=100)
    efficiency = db.Column(db.Integer, default=100)

    gender = db.Column(db.String(6))
    full_name = db.Column(db.String(100))
    seniority = db.Column(db.Integer)
    seniority_text = db.Column(db.String(50))