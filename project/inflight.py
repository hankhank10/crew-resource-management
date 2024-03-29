from flask import Blueprint, render_template, Flask, current_app, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
import secrets
from datetime import datetime, timedelta
from . import db
from . import app
from project import equipment, messaging, crew, main
from .models import Flight, FlightEvent, FlightPhase, FlightMessage, Seat
import requests
import random

inflight = Blueprint('inflight', __name__)


@inflight.route('/inflight/datadump')
@login_required
def datadump():
    
    if current_user.active_flight_id == None:
        flash ("Cannot load that page as no active flight", "danger")
        return redirect(url_for('main.dashboard'))

    flight = Flight.query.filter_by(id=current_user.active_flight_id).first()

    return render_template('inflight/datadump.html', flight=flight)


@inflight.route('/inflight/dashboard')
@login_required
def dashboard():

    if current_user.active_flight_id == None:
        flash ("Cannot load that page as no active flight", "danger")
        return redirect(url_for('main.dashboard'))

    flight = Flight.query.filter_by(id=current_user.active_flight_id).first()
    # flight_phase = FlightPhase.query.filter_by(flight.phase_flight).first()

    return render_template('inflight/dashboard.html', flight=flight)


def update_plane_data(unique_reference):
    # Get the flight and work out the source ident to query Find My Plane
    flight = Flight.query.filter_by(unique_reference=unique_reference).first_or_404()
    ident = flight.source_ident

    # Pull the data from Find My Plane, return error json if there is a problem
    try:
        r = requests.get("https://findmyplane.live/api/plane/" + ident.upper())
    except:
        return {
            'status': 'error',
            'error_message': 'Requests error'
        }

    if r.status_code != 200:
        return {
            'status': 'error',
            'error_message': 'Requests error'
        }

    if 'my_plane' in r.json():

        # Log the location
        record_location_every_seconds = 10

        next_record_due = flight.last_event_recorded + timedelta(seconds=record_location_every_seconds)
        if datetime.utcnow() > next_record_due:
            log_location(flight.id, r.json()['my_plane']['current_latitude'], r.json()['my_plane']['current_longitude'], r.json()['my_plane']['current_altitude'])


        # Check if anything has changed that needs logging
        if flight.number_of_updates_received != 0:

            if flight.door_status_mode_auto == True:
                if flight.door_status == 1 and r.json()['my_plane']['door_status'] == 0:
                    change_variable_status(flight.id, 'door', 'closed')
                if flight.door_status == 0 and r.json()['my_plane']['door_status'] == 1:
                    change_variable_status(flight.id, 'door', 'open')

                    if flight.phase_flight == "Taxi to Gate":
                        log_event(flight.id, "arrived_at_gate", "pilot")
                        set_phase(flight.id, "At gate", "flight")

            if flight.no_smoking_sign == True and r.json()['my_plane']['no_smoking_sign'] == False:
                log_event(flight.id, "no_smoking_sign_turned_off", "pilot")
            if flight.no_smoking_sign == False and r.json()['my_plane']['no_smoking_sign'] == True:
                log_event(flight.id, "no_smoking_sign_turned_on", "pilot")

            if flight.seatbelt_sign == True and r.json()['my_plane']['seatbelt_sign'] == False:
                log_event(flight.id, "seatbelt_sign_turned_off", "pilot")
            if flight.seatbelt_sign == False and r.json()['my_plane']['seatbelt_sign'] == True:
                log_event(flight.id, "seatbelt_sign_turned_on", "pilot")

            if flight.phase_flight_name == "At gate":
                if r.json()['my_plane']['speed'] > 5:
                    log_event(flight.id, "begin_taxi_for_takeoff", "pilot")
                    set_phase(flight.id, "Taxi for Takeoff", "flight")

            if flight.on_ground == True and r.json()['my_plane']['on_ground'] == False:
                log_event(flight.id, "takeoff", "pilot")
                set_phase(flight.id, "Takeoff and Climb", "flight")

            if flight.on_ground == False and r.json()['my_plane']['on_ground'] == True and r.json()['my_plane']['current_speed'] < 100:
                log_event(flight.id, "landing", "pilot")
                set_phase(flight.id, "Taxi to Gate", "flight")

        else:
            flight.door_status = r.json()['my_plane']['door_status']

        # Update plane details
        flight.current_altitude = r.json()['my_plane']['current_altitude']
        flight.current_speed = r.json()['my_plane']['current_speed']
        flight.on_ground = r.json()['my_plane']['on_ground']
        flight.seatbelt_sign = r.json()['my_plane']['seatbelt_sign']
        flight.no_smoking_sign = r.json()['my_plane']['no_smoking_sign']
        flight.parking_brake = r.json()['my_plane']['parking_brake']
        flight.gear_handle_position = r.json()['my_plane']['gear_handle_position']
        flight.number_of_updates_received = flight.number_of_updates_received + 1

        new_event_to_report = None
        if flight.new_event != None:
            new_event_to_report = flight.new_event
            flight.new_event = None

        db.session.commit()
    else:
        print ("my_plane not found in JSON")

    # Perform application logic

    # Update all the passengers
    passengers = Seat.query.filter_by(flight=flight.id).all()
    waiting_to_board = 0
    boarding = 0
    on_board = 0
    deboarding = 0
    deboarded = 0
    seated_count = 0
    unseated_count = 0
    occupied_count = 0
    empty_count = 0
    for passenger in passengers:
        if passenger.status == "Waiting to Board": waiting_to_board = waiting_to_board + 1
        if passenger.status == "Boarding": boarding = boarding + 1
        if passenger.status == "Boarded": on_board = on_board + 1
        if passenger.status == "Deboarding": deboarding = deboarding + 1
        if passenger.status == "Deboarded": deboarded = deboarded + 1

        if passenger.occupied == True:
            occupied_count = occupied_count + 1
            if passenger.status != "Waiting to Board":
                if passenger.is_seated == True:
                    seated_count = seated_count + 1
                else:
                    unseated_count = unseated_count + 1
        else:
            empty_count = empty_count + 1

    passenger_status = {
        'waiting_to_board': waiting_to_board,
        'boarding': boarding,
        'on_board': on_board,
        'deboarding': deboarding,
        'deboarded': deboarded,
        'total_seats': Seat.query.count(),
        'seated_false': unseated_count,
        'seated_true': seated_count,
        'occupied_seats': occupied_count,
        'empty_seats': empty_count
    }

    # Check if anything needs to be changed based on boarding status
    if flight.phase_cabin_name == "Boarding":

        if boarding + waiting_to_board == 0:
            # Boarding is now complete
            set_phase(flight.id, "Cabin Secure", phase_category="cabin")
            messaging.create_new_message_from_crew("Boarding complete, cabin secure")
            log_event(flight.id, "passenger_boarding_complete", "crew")
            crew.clear_crew_task(flight.id)

    if flight.phase_cabin_name == "Deboarding":
        if deboarding + on_board == 0:
            # Deboarding now complete
            set_phase(flight.id, "Deboarded", phase_category="cabin")
            messaging.create_new_message_from_crew("Deboarding complete Captain")
            log_event(flight.id, "passenger_deboarding_complete", "crew")
            crew.clear_crew_task(flight.id)

    # Get crew tasking details
    current_crew_task, percent_done_with_task = crew.crew_status(flight.id)


    my_plane = r.json()['my_plane']
    my_plane['door_status'] = flight.door_status

    # Return the info we want
    return_dictionary = {
        'my_plane': my_plane,
        'unread_flight_messages': current_user.unread_flight_messages,
        'phase_flight_name': flight.phase_flight_name,
        'phase_cabin_name': flight.phase_cabin_name,
        'passenger_status': passenger_status,
        'new_event': new_event_to_report,
        'crew_task': {
            'current_crew_task': current_crew_task,
            'percent_done_with_task': percent_done_with_task
        }
    }

    return return_dictionary


@inflight.route('/api/inflight/update_plane_data/<unique_reference>')
@login_required
def api_update_plane_data(unique_reference):
    return_dictionary = update_plane_data(unique_reference)
    return jsonify(return_dictionary)


def log_event(flight_id, event_name, event_initiated_by, current_latitude = None, current_longitude = None, current_altitude = None):

    if current_latitude == None or current_longitude == None or current_altitude == None:
        previous_event = FlightEvent.query.filter_by(flight=flight_id).order_by(FlightEvent.event_time.desc()).first()

        if previous_event is None:
            return "error"

        last_event = previous_event
        #print (last_event.id)

        current_latitude = last_event.current_latitude
        current_longitude = last_event.current_longitude
        current_altitude = last_event.current_altitude

    new_event = FlightEvent(
        flight=flight_id,
        event_time=datetime.utcnow(),
        event_type="other",
        event_initiated_by=event_initiated_by,
        event_name=event_name,
        current_latitude=current_latitude,
        current_longitude=current_longitude,
        current_altitude=current_altitude
    )
    db.session.add(new_event)
    db.session.flush()

    # Update the flight record
    flight = Flight.query.filter_by(id=flight_id).first()

    flight.last_event_recorded = datetime.utcnow()
    flight.is_active = True
    flight.new_event = new_event.event_description

    db.session.commit()

    return


def log_location(flight_id, current_latitude, current_longitude, current_altitude):
    new_event = FlightEvent (
        flight=flight_id,
        event_time=datetime.utcnow(),
        event_type="location_update",
        event_initiated_by = "simulator",
        event_name="location_update",
        current_latitude=current_latitude,
        current_longitude=current_longitude,
        current_altitude=current_altitude
    )
    db.session.add(new_event)

    flight = Flight.query.filter_by(id=flight_id).first()
    flight.last_event_recorded = datetime.utcnow()
    flight.is_active = True

    db.session.commit()
    return


@inflight.route('/api/events/')
@inflight.route('/api/events/<event_type>')
@login_required
def flight_events(event_type = None):

    if current_user.active_flight_id == None:
        flash ("Cannot load that page as no active flight", "danger")
        return redirect(url_for('main.dashboard'))
    
    if event_type is None:
        events = FlightEvent.query.filter_by(flight=current_user.active_flight_id).all()
    else:
        events = FlightEvent.query.filter_by(flight=current_user.active_flight_id, event_type=event_type).all()

    if events is None:
        return jsonify({'status': 'error'})

    event_list = []
    for event in events:

        event_dictionary = {
            'event_time': event.event_time,
            'event_type': event.event_type,
            'current_latitude': event.current_latitude,
            'current_longitude': event.current_longitude,
            'current_altitude': event.current_altitude,
            'event_initiated_by': event.event_initiated_by,
            'event_name': event.event_name
        }
        event_list.append(event_dictionary)

    return jsonify({
        'status': 'success',
        'count': len(event_list),
        'events': event_list
    })


@inflight.route('/inflight/chart')
def chart():
    
    if current_user.active_flight_id == None:
        flash ("Cannot load that page as no active flight", "danger")
        return redirect(url_for('main.dashboard'))

    return render_template('/inflight/chart.html')


def chart_altitude():
    flight_events = FlightEvent.query.filter_by(flight=current_user.active_flight_id).all()

    location_update_list = []
    other_event_list = []
    for flight_event in flight_events:
        x = datetime.timestamp(flight_event.event_time) * 1000
        y = flight_event.current_altitude
        location_update_list.append({
            'x': x,
            'y': y
        })

        if flight_event.event_type == "other":
            other_event_dictionary = {
                'x': x,
                'y': y,
                'event_name': flight_event.event_name,
                'event_description': flight_event.event_description
            }
            other_event_list.append(other_event_dictionary)

    return {
        'location_updates': location_update_list,
        'other_events': other_event_list
    }


@inflight.route('/api/chart/altitude')
def api_chart_altitude():

    if current_user.active_flight_id == None:
        flash ("Cannot load that page as no active flight", "danger")
        return redirect(url_for('main.dashboard'))

    chart_dictionary = chart_altitude()

    return jsonify ({
        'status': 'success',
        'location_updates': chart_dictionary['location_updates'],
        'other_events': chart_dictionary['other_events']
    })


@inflight.route('/helper/events/')
@login_required
def helper_events():

    if current_user.active_flight_id == None:
        return "Cannot load the page as no active flight", 404

    events = FlightEvent.query.filter_by(flight=current_user.active_flight_id, event_type="other").all()

    return render_template('/inflight/events_helper.html', events = events)


@inflight.route('/api/inflight/set_flight_phase')
@login_required
def api_set_phase():

    if current_user.active_flight_id == None:
        return "Cannot load the page as no active flight", 404

    flight_id = current_user.active_flight_id
    phase_setting = request.args.get('phase_to_set')

    set_phase(flight_id, phase_setting, "flight")

    return "ok"


@inflight.route('/api/inflight/set_variable_status')
@login_required
def api_set_door_status():

    if current_user.active_flight_id is None:
        return "Cannot load the page as no active flight", 404

    variable_type = request.args.get('variable_type')
    variable_value = request.args.get('variable_value')

    print (variable_type)

    change_variable_status(current_user.active_flight_id, variable_type, variable_value, True)

    return "ok"


def change_variable_status(flight_id, variable_type, variable_value, set_to_manual = False):

    print (variable_value)

    flight = Flight.query.filter_by(id = flight_id).first()

    if flight is None:
        return None

    if variable_type == 'door':

        if variable_value.lower() == "close manually" or variable_value.lower() == "closed":
            flight.door_status = 0
            log_event(flight.id, "cabin_door_closed", "pilot")

        if variable_value.lower() == "open manually" or variable_value.lower() == "open":
            flight.door_status = 1
            log_event(flight.id, "cabin_door_opened", "pilot")

        if set_to_manual:
            flight.door_status_mode_auto = False

        db.session.commit()

    return


def set_phase(flight_id, phase_name, phase_category="flight"):
    # Get the flight
    flight = Flight.query.filter_by(id=flight_id).first()

    if flight is None:
        return None

    # See if there is a current phase...
    current_phase = None
    if phase_category == "flight":
        current_phase = FlightPhase.query.filter_by(id=flight.phase_flight).first()

    if phase_category == "cabin":
        current_phase = FlightPhase.query.filter_by(id=flight.phase_cabin).first()

    if phase_category == "seatbelt_sign":
        current_phase = FlightPhase.query.filter_by(id=flight.phase_seatbelt_sign).first()

    # ... and if so end it
    if current_phase is not None:
        current_phase.end_time = datetime.utcnow()
        current_phase.is_current = False

    # Create a new phase
    new_phase = FlightPhase(
        flight=flight_id,
        start_time=datetime.utcnow(),
        phase_category=phase_category,
        phase_name=phase_name,
        is_current=True
    )
    db.session.add(new_phase)
    db.session.commit()

    db.session.refresh(new_phase)

    if phase_category == "flight":
        flight.phase_flight = new_phase.id

    if phase_category == "cabin":
        flight.phase_cabin = new_phase.id

    if phase_category == "seatbelt_sign":
        flight.phase_seatbelt_sign = new_phase.id

    db.session.commit()

    # Create an event
    if phase_category == "flight":
        log_event(flight_id, "flight_phase_" + phase_name.lower(), "pilot")

    return new_phase
