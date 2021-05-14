from flask import Blueprint, render_template, Flask, current_app, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
import secrets
from datetime import datetime, timedelta
from . import db
from . import app
from project import flight_manager, passengers, crew
from project import email
from .models import Flight, FlightPhase, EquipmentType, FlightEvent, FlightMessage


cron = Blueprint('cron', __name__)


@cron.route('/cron/every_minute')
def every_minute():

    # Set old flights as inactive
    flight_manager.cron_retire_old_flights()

    # Move up passenger needs
    passengers_needing_increment = passengers.increment_passenger_needs()

    # Do crew tasks
    flights = Flight.query.filter_by(is_active = True).all()

    for flight in flights:
        crew.do_crew_task(flight.id)

    return "OK: " + str(passengers_needing_increment) + " passengers incremented"


@cron.route('/cron/test_email')
def test_email():
    email.send_verification_code("test@test.com")
    return "OK"
