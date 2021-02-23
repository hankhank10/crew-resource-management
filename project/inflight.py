from flask import Blueprint, render_template, Flask, current_app, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
import secrets
from datetime import datetime
from . import db
from . import app
from project import equipment
from .models import Flight


inflight = Blueprint('inflight', __name__)

@inflight.route('/inflight/datadump')
@login_required
def datadump():

    flight = Flight.query.filter_by(id = current_user.active_flight_id).first()

    #return flight.equipment_full_name

    return render_template('inflight/datadump.html', flight=flight)
