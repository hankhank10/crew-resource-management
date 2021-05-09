from flask import Blueprint, render_template, Flask, current_app, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import query
from . import db
from . import app
from project import equipment, inflight, passengers, seatmapper, crew, messaging
from .models import Flight, FlightPhase, EquipmentType, FlightEvent, FlightMessage


flight_manager = Blueprint('flight_manager', __name__)

@flight_manager.route('/flight')
@login_required
def view_list():

    flights = Flight.query.filter_by(user = current_user.id).all()

    return render_template('/flight/flight_list.html', flight_list=flights)


@flight_manager.route('/flight/new', methods=['GET', 'POST'])
@login_required
def new():

    if request.method == "GET":
        equipment_list = EquipmentType.query.all()
        return render_template('flight/new_flight.html', equipment_list=equipment_list)

    if request.method == "POST":

        relevant_equipment = EquipmentType.query.filter_by(full_name=request.form['equipment_selector']).first()
        if not relevant_equipment:
            flash("Error finding that equipment spec", "danger")
            return render_template('flight/new_flight.html', equipment_list=equipment.equipment_list)

        try:
            unique_reference = datetime.today().strftime('%Y%m%d') + "-" + secrets.token_hex(10).upper()

            flight = Flight (
                user=current_user.id,
                unique_reference=unique_reference,
                departure_code=request.form['departure_airport_code'],
                departure_name=request.form['departure_airport_name'],
                destination_code=request.form['destination_airport_code'],
                destination_name=request.form['destination_airport_name'],
                equipment_full_name=request.form['equipment_selector'],
                equipment_manufacturer=request.form['equipment_manufacturer'],
                equipment_operator=request.form['equipment_operator'],
                equipment_model=request.form['equipment_model'] + " " + request.form['equipment_variant'],
                passengers_first_class=int(request.form['first_class_actual']),
                passengers_business_class=int(request.form['business_class_actual']),
                passengers_premium_class=int(request.form['premium_class_actual']),
                passengers_economy_class=int(request.form['economy_class_actual']),
                cabin_crew_count=int(request.form['cabin_crew_actual']),
                seatmap_text=relevant_equipment.seatmap_text,
                number_of_rows=relevant_equipment.number_of_rows,
                number_of_seats_across=relevant_equipment.number_of_seats_across,
                number_of_toilets=relevant_equipment.number_of_toilets,
                last_event_recorded=datetime.utcnow(),
            )

            db.session.add(flight)

            current_user.tutorial_created_flight_plan = True
            db.session.commit()
        except:
            flash ("Error creating new flight plan", "danger")
            return render_template('flight/new_flight.html', equipment_list=equipment.equipment_list)

        flash("New flight plan created", "success")

        return redirect(url_for('flight_manager.view_list'))


@flight_manager.route('/flight/delete/<unique_reference>')
@login_required
def delete(unique_reference):

    flight = Flight.query.filter_by(unique_reference=unique_reference).first_or_404()
    
    if flight.user != current_user.id:
        flash("Not authorised to delete that flight plan", "danger")
        return redirect(url_for('flight_manager.view_list'))

    db.session.delete(flight)
    db.session.commit()

    flash("Flight plan successfully deleted", "success")
    return redirect(url_for('flight_manager.view_list'))


@flight_manager.route('/flight/duplicate/<unique_reference>')
@login_required
def duplicate(unique_reference):

    old_flight = Flight.query.filter_by(unique_reference=unique_reference).first_or_404()

    new_unique_reference = datetime.today().strftime('%Y%m%d') + "-" + secrets.token_hex(10).upper()

    new_flight = Flight(
        user=current_user.id,
        unique_reference=new_unique_reference,
        departure_code=old_flight.departure_code,
        departure_name=old_flight.departure_name,
        destination_code=old_flight.destination_code,
        destination_name=old_flight.destination_name,
        equipment_full_name=old_flight.equipment_full_name,
        equipment_manufacturer=old_flight.equipment_manufacturer,
        equipment_operator=old_flight.equipment_operator,
        equipment_model=old_flight.equipment_model,
        passengers_first_class=old_flight.passengers_first_class,
        passengers_business_class=old_flight.passengers_business_class,
        passengers_premium_class=old_flight.passengers_premium_class,
        passengers_economy_class=old_flight.passengers_economy_class,
        cabin_crew_count=old_flight.cabin_crew_count,
        seatmap_text=old_flight.seatmap_text,
        number_of_rows=old_flight.number_of_rows,
        number_of_seats_across=old_flight.number_of_seats_across,
        started=False,
        completed=False,
        is_active=False,
        last_event_recorded=datetime.utcnow()
    )

    db.session.add(new_flight)
    db.session.commit()

    flash("Flight plan duplicated", "success")

    return redirect(url_for('flight_manager.view_list'))


@flight_manager.route('/pre-flight/<unique_reference>')
@login_required
def pre_flight(unique_reference):

    flight = Flight.query.filter_by(unique_reference=unique_reference).first_or_404()

    return render_template('flight/pre_flight_checklist.html', flight_plan=flight)


@flight_manager.route('/pre-flight/<unique_reference>/start/<ident>')
@login_required
def start_flight(unique_reference, ident):

    if unique_reference is None or ident is None:
        return "error", 404

    # Find the relevant flight
    flight = Flight.query.filter_by(unique_reference=unique_reference).first_or_404()

    # Add the findmyplane_ident to that flight
    flight.source = "findmyplane"
    flight.source_ident = ident
    flight.last_event_recorded = datetime.utcnow() - timedelta(seconds=120)
    flight.is_active = True
    flight.started = True
    flight.number_of_updates_received = 0
    flight.current_crew_task = "Resting"
    db.session.commit()

    # Delete previous events and phases
    FlightEvent.query.filter_by(flight=flight.id).delete()
    FlightPhase.query.filter_by(flight=flight.id).delete()
    FlightMessage.query.filter_by(flight=flight.id).delete()

    # Create the phases
    inflight.set_phase(flight.id, "At Gate", "flight")
    inflight.set_phase(flight.id, "Pre-Boarding", "cabin")

    # Fill the flight with passengers and crew
    passengers.fill_flight_with_passengers(flight.id)
    crew.fill_flight_with_crew(flight.id)

    # Set the current user's flight
    current_user.active_flight_id = flight.id
    current_user.tutorial_started_flight = True
    db.session.commit()

    messaging.create_new_message_from_crew(
        messaging.intro_message_content(first_time=True),
        read=False,
        flight_id=flight.id
    )

    return redirect(url_for('inflight.dashboard'))


@flight_manager.route('/inflight/end')
@login_required
def end_flight():

    if current_user.active_flight_id is None:
        flash("No active flight", "danger")
        return redirect(url_for('main.dashboard'))

    current_flight = Flight.query.filter_by(id = current_user.active_flight_id).first_or_404()

    current_flight.completed = True
    current_flight.is_active = False

    current_user.active_flight_id = None

    db.session.commit()

    flash ("Flight ended", "success")
    return redirect(url_for('main.dashboard'))
    

def cron_retire_old_flights():

    active_flights = Flight.query.filter_by(is_active=True).all()

    cutoff_time = datetime.utcnow() - timedelta(minutes=10)

    for flight in active_flights:
        if flight.last_event_recorded < cutoff_time:
            flight.is_active = False

    db.session.commit()
    return
