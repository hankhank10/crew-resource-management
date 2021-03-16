from flask import Blueprint, render_template, Flask, current_app, jsonify
from flask_login import login_required, current_user
from . import db
from . import app
from .models import Flight, Seat, Passenger
import random
from project import name_generator, seatmapper


passengers = Blueprint('passengers', __name__)


def create_new_passenger():

    age = random.randint(18, 65)

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
        first_name = name_generator.first_name(),
        second_name = name_generator.second_name(),
        age = age,
        frequent_flyer_status = frequent_flyer_status
    )
    db.session.add(new_passenger)
    db.session.commit()


@passengers.route('/backend/create_new_passengers/<how_many>')
def create_new_passengers(how_many=1):

    for a in range(1, int(how_many)):
        create_new_passenger()

    return "Created " + str(how_many) + " new passengers"


@passengers.route('/inflight/passengers')
def list():

    return render_template('/passengers/passengers_list.html')


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
            'seat_type': " ",
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
        'occupied_seats': occupied_seat_output_list,
#        'empty_seats': empty_seat_output_list
    }

    return jsonify(output_dictionary)


def board_passengers(flight_id):

    passengers_to_load_per_minute = 20
    second_between_each_passengers = 60 / passengers_to_load_per_minute

    seconds_takes_to_board = 60

    passengers = Seat.query.filter_by(flight_id = flight_id).all()

    offset = 1
    #for passenger in passengers:
    #    seconds_from_now_to_load =


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

            # If
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






# DEBUG ONLY
#@passengers.route('/passengers/populate')
#def test_passengers_populate():
#
#    return fill_flight_with_passengers(current_user.active_flight_id)

