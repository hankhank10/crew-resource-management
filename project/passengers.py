from flask import Blueprint, render_template, Flask, current_app, jsonify
from flask_login import login_required, current_user
from . import db
from . import app
from .models import Flight, Seat, Passenger
import random
from project import name_generator, seatmapper, inflight, crew
from datetime import datetime, timedelta


passengers = Blueprint('passengers', __name__)


def create_new_passenger():

    age = random.randint(18, 65)

    gender = random.choices([
        "Male",
        "Female"
    ])[0]

    frequent_flyer_status = random.choices([
        0,  #None
        1,  #Blue
        2,  #Bronze
        3,  #Silver
        4,  #Gold,
        5,  #VIP
    ],[
        100,
        50,
        20,
        10,
        5,
        1
    ])[0]

    new_passenger = Passenger(
        first_name = name_generator.first_name(gender),
        second_name = name_generator.second_name(),
        age = age,
        frequent_flyer_status = frequent_flyer_status,
        gender = gender
    )
    db.session.add(new_passenger)
    db.session.commit()


@passengers.route('/backend/create_new_passengers/<how_many>')
def create_new_passengers(how_many=1):

    for a in range(1, int(how_many)):
        create_new_passenger()

    return "Created " + str(how_many) + " new passengers"


@passengers.route('/inflight/passengers/')
def list():

    return render_template('/passengers/passengers_list.html')


@passengers.route('/inflight/passengers/seatmap')
def show_seatmap_page():

    return render_template('/passengers/seatmap.html')


@passengers.route('/api/passengers/<unique_reference>/<seat_number>')
def api_passenger_details(unique_reference, seat_number):

    flight = Flight.query.filter_by(unique_reference=unique_reference).first_or_404()
    seat = Seat.query.filter_by(flight = flight.id, seat_number = seat_number).first_or_404()

    seat_dictionary = {
        'manifest_number': seat.manifest_number,
        'x': seat.x,
        'y': seat.y,
        'seat_type': seat.seat_type,
        'seat_type_text': seat.seat_type_text,
        'occupied': seat.occupied,
        'occupied_by_id': seat.occupied_by,
        'phase': seat.phase,
        'status': seat.status,
        'activity': seat.activity,
        'is_seated': seat.is_seated,
        'status_bladder_need': seat.status_bladder_need,
        'status_bladder_need_text': seat.status_bladder_need_text,
        'status_hunger': seat.status_hunger,
        'status_hunger_text': seat.status_hunger_text,
        'status_thirst': seat.status_thirst,
        'status_thirst_text': seat.status_thirst_text,
        'full_name': seat.full_name,
        'frequent_flyer_status': seat.frequent_flyer_status,
        'frequent_flyer_status_text': seat.frequent_flyer_status_text,
        'seat_number': seat.seat_number,
        'gender': seat.gender
    }
    return jsonify(seat_dictionary)



@passengers.route('/api/passengers/list/<unique_reference>')
def api_list(unique_reference):

    flight = Flight.query.filter_by(unique_reference=unique_reference).first()

    if flight is None:
        return jsonify ({
            'status': 'error',
            'error': 'flight not found'
        })

    occupied_seat_list = Seat.query.filter_by(flight = flight.id, occupied = True).all()

    occupied_seat_output_list = []
    empty_seat_output_list = []

    occupied_seat_count = 0
    empty_seat_count = 0

    # Occupied seats
    for seat in occupied_seat_list:
        occupied_seat_dictionary = {
            'manifest_number': seat.manifest_number,
            'x': seat.x,
            'y': seat.y,
            'seat_type': seat.seat_type,
            'seat_type_text': seat.seat_type_text,
            'occupied': seat.occupied,
            'occupied_by_id': seat.occupied_by,
            'phase': seat.phase,
            'status': seat.status,
            'activity': seat.activity,
            'is_seated': seat.is_seated,
            'status_bladder_need': seat.status_bladder_need,
            'status_hunger': seat.status_hunger,
            'status_thirst': seat.status_thirst,
            'full_name': seat.full_name,
            'frequent_flyer_status': seat.frequent_flyer_status,
            'frequent_flyer_status_text': seat.frequent_flyer_status_text,
            'seat_number': seat.seat_number
        }
        occupied_seat_output_list.append(occupied_seat_dictionary)
        occupied_seat_count = occupied_seat_count + 1

    # Empty seats
    empty_seat_list = Seat.query.filter_by(flight = flight.id, occupied = False).all()
    for empty_seat in empty_seat_list:
        empty_seat_dictionary = {
            'x': empty_seat.x,
            'y': empty_seat.y,
            'seat_number': empty_seat.seat_number,
            'seat_type': empty_seat.seat_type,
            'seat_type_text': "Empty seat",
            'occupied': False
        }
        empty_seat_output_list.append(empty_seat_dictionary)
        empty_seat_count = empty_seat_count + 1

    output_dictionary = {
        'status': 'success',
        'seat_count_empty': empty_seat_count,
        'seat_count_occupied': occupied_seat_count,
        'seat_count_total': occupied_seat_count + empty_seat_count,
        'number_of_rows': flight.number_of_rows,
        'number_of_seats_across': flight.number_of_seats_across,
        'passengers_first_class': flight.passengers_first_class,
        'passengers_business_class': flight.passengers_business_class,
        'passengers_premium_class': flight.passengers_premium_class,
        'passengers_economy_class': flight.passengers_economy_class,
        'occupied_seats': occupied_seat_output_list,
        'empty_seats': empty_seat_output_list
    }

    return jsonify(output_dictionary)


def board_passengers(flight_id):

    passengers_to_load_per_minute = 120
    seconds_takes_to_board = 60

    second_between_each_passengers = 60 / passengers_to_load_per_minute


    passengers = Seat.query.filter_by(flight = flight_id, occupied = True).all()

    offset = 1
    for passenger in passengers:
        seconds_from_now_to_start_boarding = second_between_each_passengers * offset
        seconds_from_now_to_seated = seconds_from_now_to_start_boarding + seconds_takes_to_board

        time_start_boarding = datetime.utcnow() + timedelta(seconds=seconds_from_now_to_start_boarding)
        time_to_be_seated = datetime.utcnow() + timedelta(seconds=seconds_from_now_to_seated)

        passenger.time_start_boarding = time_start_boarding
        passenger.time_seated = time_to_be_seated

        offset = offset + 1

    db.session.commit()

    # Log event
    inflight.log_event(flight_id, "start_boarding_passengers", "pilot")

    # Set crew status
    crew.assign_crew_task(flight_id, "Welcoming passengers")


def deboard_passengers(flight_id):
    passengers_to_unload_per_minute = 120
    seconds_takes_to_deboard = 60

    second_between_each_passengers = 60 / passengers_to_unload_per_minute

    passengers = Seat.query.filter_by(flight=flight_id, occupied=True).all()

    offset = 1
    for passenger in passengers:
        seconds_from_now_to_start_deboarding = second_between_each_passengers * offset
        seconds_from_now_to_be_deboarded = seconds_from_now_to_start_deboarding + seconds_takes_to_deboard

        time_started_deboarding = datetime.utcnow() + timedelta(seconds=seconds_from_now_to_start_deboarding)
        time_deboarded = datetime.utcnow() + timedelta(seconds=seconds_from_now_to_be_deboarded)

        passenger.time_started_deboarding = time_started_deboarding
        passenger.time_deboarded = time_deboarded

        offset = offset + 1

    db.session.commit()

    # Log event
    inflight.log_event(flight_id, "start_deboarding_passengers", "pilot")

    # Set crew status
    crew.assign_crew_task(flight_id, "Deboarding passengers")




def fill_flight_with_passengers(flight_id):

    flight = Flight.query.filter_by(id=flight_id).first()

    if flight is None:
        return "error"

    # Delete any previous passengers
    Seat.query.filter_by(flight = flight_id).delete()

    # Parse the seatmap for the flight
    seatmap_object = seatmapper.load_seatmap(flight.seatmap_text)

    # Work out how many potential passengers there are available to choose from
    how_many_passengers_exist = Passenger.query.count()

    # Reset all the lists before we start the loop
    list_of_already_loaded_passengers = []
    manifest_number = 1

    # Specify the list of classes we need to run through
    list_of_class_types = ['F', 'B', 'P', 'E']

    for class_code in list_of_class_types:
        if class_code == "F": number_to_load = flight.passengers_first_class
        if class_code == "B": number_to_load = flight.passengers_business_class
        if class_code == "P": number_to_load = flight.passengers_premium_class
        if class_code == "E": number_to_load = flight.passengers_economy_class

        seat_list_for_this_class = seatmapper.get_seats_by_type(seatmap_object, class_code, True)
        seat_count_for_this_class = len(seat_list_for_this_class)

        # Populate each class
        for a in range(0, seat_count_for_this_class):

            if a > number_to_load-1:
                new_seat = Seat(
                    flight = flight_id,
                    x=seat_list_for_this_class[a]['x'],
                    y=seat_list_for_this_class[a]['y'],
                    seat_number=seat_list_for_this_class[a]['seat_number'],
                    seat_type=seat_list_for_this_class[a]['seat_type'],
                    phase="Empty seat",
                    occupied=False
                )
                db.session.add(new_seat)
                db.session.commit()
            else:
                can_this_passenger_be_loaded = False

                while can_this_passenger_be_loaded == False:
                    selected_passenger_id = random.randint(1, how_many_passengers_exist)

                    if selected_passenger_id not in list_of_already_loaded_passengers:
                        can_this_passenger_be_loaded = True
                        list_of_already_loaded_passengers.append(selected_passenger_id)
                        new_seat = Seat(
                            flight = flight_id,
                            x = seat_list_for_this_class[a]['x'],
                            y = seat_list_for_this_class[a]['y'],
                            manifest_number = manifest_number,
                            seat_number=seat_list_for_this_class[a]['seat_number'],
                            seat_type=class_code,
                            occupied=True,
                            occupied_by=selected_passenger_id,
                            phase="Pre Flight",
                            is_seated=False,
                            status_bladder_need=random.randint(20,80),
                            status_hunger=random.randint(20,80),
                            status_thirst=random.randint(20,80)
                        )
                        db.session.add(new_seat)
                        db.session.commit()
                        manifest_number = manifest_number + 1

    return "ok"


def increment_passenger_needs():

    increment_passenger_needs_every = 5  #minutes

    bladder_need_time = 120  #minutes to go from 0 to 100
    hunger_need_time = 360  #minutes
    thirst_need_time = 120  #minutes

    passengers_needing_increment = Seat.query.filter(Seat.next_increment_due < datetime.utcnow()).all()

    for passenger in passengers_needing_increment:

        bladder_need_increment = (increment_passenger_needs_every / bladder_need_time) * 100
        hunger_need_increment = (increment_passenger_needs_every / hunger_need_time) * 100
        thirst_need_increment = (increment_passenger_needs_every / thirst_need_time) * 100

        passenger.status_bladder_need = min(passenger.status_bladder_need + bladder_need_increment, 100)
        passenger.status_hunger = min(passenger.status_hunger + hunger_need_increment, 100)
        passenger.status_thirst = min(passenger.status_thirst + thirst_need_increment, 100)

        passenger.next_increment_due = datetime.utcnow() + timedelta(minutes=increment_passenger_needs_every)

    print ("Updated " + str(len(passengers_needing_increment)) + " passenger records")
    db.session.commit()
