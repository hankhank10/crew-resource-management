from flask import Blueprint, render_template, Flask, current_app, jsonify
from flask_login import login_required, current_user
from . import db
from . import app
from .models import Flight, CrewMember, CrewPopulation
import random
from project import name_generator, seatmapper, inflight
from datetime import datetime, timedelta

crew = Blueprint('crew', __name__)


def create_new_crew_member():
    gender = random.choices([
        "Male",
        "Female"
    ])[0]

    seniority = random.choices([
        0,
        1,
        2,
    ], [
        100,
        50,
        10,
    ])[0]

    efficiency = random.randint(80, 120)

    new_crew = CrewPopulation(
        first_name=name_generator.first_name(gender),
        second_name=name_generator.second_name(),
        gender=gender,
        seniority=seniority,
        efficiency=efficiency
    )
    #print ("Created!")
    db.session.add(new_crew)
    db.session.commit()


@crew.route('/backend/create_new_crew/<how_many>')
def create_new_crew_members(how_many=1):

    for a in range(1, int(how_many)):
        create_new_crew_member()
        print (str(a))

    return "Created " + str(how_many) + " new crew"


def fill_flight_with_crew(flight_id):

    flight = Flight.query.filter_by(id=flight_id).first()

    if flight is None:
        return "error"

    # Delete any previous crew
    CrewMember.query.filter_by(flight = flight_id).delete()

    # Populate new crew
    how_many_crew_exist = CrewPopulation.query.count()

    list_of_already_loaded_crew = []

    for a in range(1, flight.cabin_crew_count):

        can_this_crew_be_loaded = False
        while can_this_crew_be_loaded == False:
            selected_crew_id = random.randint(1, how_many_crew_exist)
            selected_crew = CrewPopulation.query.filter_by(id = selected_crew_id).first()

            if selected_crew is not None:

                if selected_crew_id not in list_of_already_loaded_crew:

                    can_this_crew_be_loaded = True
                    list_of_already_loaded_crew.append(selected_crew_id)

                    new_crew = CrewMember (
                        flight = flight_id,
                        identity = selected_crew_id,
                        energy = selected_crew.efficiency,
                        efficiency = selected_crew.efficiency,
                        gender = selected_crew.gender,
                        full_name = selected_crew.full_name,
                        seniority = selected_crew.seniority,
                        seniority_text = selected_crew.seniority_text
                    )
                    db.session.add(new_crew)

    db.session.commit()
    return