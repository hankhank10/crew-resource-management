from flask import Blueprint, render_template, Flask, current_app, jsonify
from flask_login import login_required, current_user
from . import db
from . import app
from .models import Flight, CrewMember, CrewPopulation, Seat
import random
from project import name_generator, seatmapper, inflight, messaging
from datetime import date, datetime, timedelta

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

    for a in range(0, flight.cabin_crew_count):

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


@login_required
@crew.route('/crew/current')
def current_crew():

    return render_template('crew/current_crew.html')


def assign_crew_task(flight_id, task_name):

    flight = Flight.query.filter_by(id = flight_id).first()

    flight.current_crew_task = task_name
    flight.current_crew_task_completed_as_far_as = 0

    db.session.commit()


def clear_crew_task(flight_id):

    flight = Flight.query.filter_by(id = flight_id).first()

    if flight.current_crew_task == "Drinks service":
        messaging.create_new_message_from_crew("Drinks service complete")

    if flight.current_crew_task == "Meal service":
        messaging.create_new_message_from_crew("Meal service complete")


    flight.current_crew_task = "Resting"
    flight.current_crew_task_completed_as_far_as = 0

    db.session.commit()


def do_crew_task(flight_id):

    flight = Flight.query.filter_by(id=flight_id).first()

    if flight.current_crew_task == "Resting":
        return

    if flight.current_crew_task == "Boarding passengers":
        return

    how_many_passengers = flight.passengers_total
    completed_as_far_as = flight.current_crew_task_completed_as_far_as

    if completed_as_far_as >= how_many_passengers:
        clear_crew_task(flight_id)

    # Actually do the tasks

    how_many_crew = flight.cabin_crew_count

    seconds_since_last_cron = 30
    minutes_since_last_cron = seconds_since_last_cron / 60

    drinks_served_per_minute = 4 * how_many_crew
    meals_served_per_minute = 2 * how_many_crew


    if flight.current_crew_task == "Drinks service":
        things_done_this_time = drinks_served_per_minute * minutes_since_last_cron

    if flight.current_crew_task == "Meal service":
        things_done_this_time = meals_served_per_minute * minutes_since_last_cron


    things_done_this_time = int(things_done_this_time)

    for a in range(completed_as_far_as + 1, completed_as_far_as + 1 + things_done_this_time):
        seat = Seat.query.filter_by(flight = flight_id, manifest_number = a).first()

        if flight.current_crew_task == "Drinks service": 
            seat.status_thirst = 0

        if flight.current_crew_task == "Meal service":
            seat.status_hunger = 0
        
        db.session.commit()
    
    flight.current_crew_task_completed_as_far_as = flight.current_crew_task_completed_as_far_as + things_done_this_time
    db.session.commit()

    return


@login_required
@crew.route('/helper/crew')
def helper():

    current_crew = CrewMember.query.filter_by(flight = current_user.active_flight_id).all()

    current_crew_task, percent_done_with_task = crew_status(current_user.active_flight_id)

    return render_template('/crew/crew_helper.html', current_crew = current_crew, current_crew_task = current_crew_task, percent_done_with_task = percent_done_with_task)


def crew_status(flight_id):

    current_flight = Flight.query.filter_by(id = flight_id).first()

    current_crew_task = current_flight.current_crew_task
    
    percent_done_with_task = None

    if current_crew_task == "Resting":
        percent_done_with_task = 500

    if current_crew_task == "Welcoming passengers":
        percent_done_with_task = 500

    if percent_done_with_task == None:
        percent_done_with_task = (current_flight.current_crew_task_completed_as_far_as / current_flight.passengers_total) * 100
        percent_done_with_task = int(percent_done_with_task)

        current_crew_task = current_crew_task + " (" + str(percent_done_with_task) + "% complete)"

    return current_crew_task, percent_done_with_task



@login_required
@crew.route('/api/crew/check')
def api_crew_status():
    current_flight = Flight.query.filter_by(id = current_user.active_flight_id).first()

    

