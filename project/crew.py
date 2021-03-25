from flask import Blueprint, render_template, Flask, current_app, jsonify
from flask_login import login_required, current_user
from . import db
from . import app
from .models import Flight, CrewMember, CrewPopulation
import random
from project import name_generator, seatmapper, inflight
from datetime import datetime, timedelta

crew = Blueprint('crew', __name__)


def create_new_crew():
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
def create_new_crew_endpoint(how_many=1):

    for a in range(1, int(how_many)):
        create_new_crew()
        print (str(a))

    return "Created " + str(how_many) + " new crew"
