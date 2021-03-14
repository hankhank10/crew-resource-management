from flask import Blueprint, render_template, Flask, current_app, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
import secrets
from datetime import datetime
from . import db
from . import app
from project import equipment, inflight, passengers
from .models import Flight, FlightPhase


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
        return render_template('flight/new_flight.html', equipment_list=equipment.equipment_list)

    if request.method == "POST":

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
                cabin_crew_count=int(request.form['cabin_crew_actual'])
            )

            db.session.add(flight)
            db.session.commit()
        except:
            flash ("Error creating new flight plan", "danger")
            return render_template('flight/new_flight.html', equipment_list=equipment.equipment_list)

        flash("New flight plan created", "success")

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
    db.session.commit()

    # Create the phases
    inflight.set_phase(flight.id, "At Gate", "flight")
    inflight.set_phase(flight.id, "Pre-Boarding", "cabin")

    # Fill the flight with passengers
    passengers.fill_flight_with_passengers(flight.id)

    # Set the current user's flight
    current_user.active_flight_id = flight.id
    db.session.commit()

    return redirect(url_for('inflight.dashboard'))


