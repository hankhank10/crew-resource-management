from flask import Blueprint, render_template, Flask, current_app, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
import secrets
from datetime import datetime
from . import db
from . import app
from project import equipment
from .models import Flight, FlightEvent, FlightPhase
import requests


inflight = Blueprint('inflight', __name__)


@inflight.route('/inflight/datadump')
@login_required
def datadump():

    flight = Flight.query.filter_by(id=current_user.active_flight_id).first()

    return render_template('inflight/datadump.html', flight=flight)


@inflight.route('/inflight/events')
@login_required
def flight_events():
    flight_events = FlightEvent.query.filter_by(flight=current_user.active_flight_id, event_type="other").all()
    location_updates = FlightEvent.query.filter_by(flight=current_user.active_flight_id, event_type="location_update").all()
    #location_updates = FlightEvent.query.all()

    print (len(location_updates))

    return render_template('inflight/events.html', flight_events=flight_events, location_updates=location_updates)


@inflight.route('/api/inflight/update_plane_data/<unique_reference>')
@login_required
def api_update_plane_data(unique_reference):

    # Get the flight and work out the ident
    flight = Flight.query.filter_by(unique_reference=unique_reference).first_or_404()
    ident = flight.source_ident


    # Pull the data from Find My Plane, return error json if there is a problem
    try:
        r = requests.get("https://findmyplane.live/api/plane/" + ident.upper())
    except:
        return jsonify({'status': 'error', 'error_message': 'Requests error'})

    if r.status_code != 200:
        return jsonify({'status': 'error', 'error_message': 'Requests error'})


    # Create new flight events
    flight_event = FlightEvent(
        flight=flight.id,
        event_time=datetime.utcnow(),
        event_type="location_update",
        current_latitude=r.json()['my_plane']['current_latitude'],
        current_longitude=r.json()['my_plane']['current_longitude']
    )
    db.session.add(flight_event)
    db.session.commit()

    # Perform application logic

    # Return the info we want
    return_dictionary = {
        'my_plane': r.json()['my_plane']
    }

    return return_dictionary


@inflight.route('/api/inflight/log_event/<unique_reference>', methods=['POST'])
@login_required
def api_log_event(unique_reference):

    relevant_flight = Flight.query.filter_by(unique_reference=unique_reference).first_or_404()

    content_received = request.get_json()

    if content_received['event_code'] == "passenger_announcement":
        event_name = "Announcement by pilot to the passengers"

    if 'event_name' in content_received:
        event_name = content_received['event_name']

    new_event = FlightEvent (
        flight=relevant_flight.id,
        event_type="other",
        event_initiated_by=content_received['event_initiated_by'],
        event_code=content_received['event_code'],
        event_name=event_name,
        event_description=content_received['event_description'],
    )
    db.session.add(new_event)
    db.session.commit()

    return jsonify({'status': 'success'})


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

    return new_phase
