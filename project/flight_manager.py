from flask import Blueprint, render_template, Flask, current_app
from flask_login import login_required, current_user
from . import db
from . import app


flight_manager = Blueprint('flight_manager', __name__)


@flight_manager.route('/flight/new')
@login_required
def dashboard():

    return render_template('flight/new_equipment.html')
