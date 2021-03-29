from flask import Blueprint, render_template, Flask, current_app, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
import secrets
from datetime import datetime, timedelta
from . import db
from . import app
from project import flight_manager, passengers
from .models import Flight, FlightPhase, EquipmentType, FlightEvent, FlightMessage


cron = Blueprint('cron', __name__)

@cron.route('/cron/every_30_seconds')
def every_30_seconds():

    # Set old flights as inactive
    flight_manager.cron_retire_old_flights()

    # Move up passenger needs
    passengers.increment_passenger_needs()

    return "OK"
