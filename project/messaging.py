from flask import Blueprint, render_template, Flask, current_app, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
import secrets
from datetime import datetime
from . import db
from . import app
from project import equipment
from .models import Flight, FlightEvent, FlightPhase, FlightMessage
import requests
import random


messaging = Blueprint('messaging', __name__)


@messaging.route('/inflight/messaging')
@messaging.route('/inflight/messaging/<message_type>')
def chat(message_type = "crew"):

    if message_type == "crew":
        messages = FlightMessage.query.filter_by(flight=current_user.active_flight_id, message_type=message_type).all()

        # Mark all this users' crew messages as read
        current_user.unread_flight_messages = 0
        db.session.commit()

    return render_template('inflight/chat.html', existing_message_list=messages)

@login_required
@messaging.route('/api/inflight/messaging/check_messages', methods=['GET'])
def check_message_count():

    return jsonify({
        'status': 'success',
        'unread_flight_messages': current_user.unread_flight_messages
    })

@login_required
@messaging.route('/api/inflight/messaging/send_message', methods=['GET'])
def send_message_from_pilot():

    if current_user.active_flight_id is None:
        return jsonify ({
            'status': 'error',
            'error_message': 'No active flight for this user'
        })

    message_to = request.args.get('message_to')
    message_content = request.args.get('message_content')

    # Store the message down
    new_message = FlightMessage(
        flight = current_user.active_flight_id,
        message_time = datetime.utcnow(),
        message_from = "pilot",
        message_type = message_to,
        message_to = message_to,
        message_content = message_content
    )
    db.session.add(new_message)
    db.session.commit()

    message_content = message_content.lower()

    # Interpret the message
    message_interpretation = "unknown"
    if message_to == "crew":

        # Coffee to flight deck
        if "coffee" in message_content: message_interpretation = "pilot_wants_coffee"
        if "tea" in message_content: message_interpretation = "pilot_wants_coffee"

        # Begin boarding
        if "commence boarding" in message_content: message_interpretation = "begin_boarding"
        if "commence the boarding" in message_content: message_interpretation = "begin_boarding"
        if "commence passenger boarding" in message_content: message_interpretation = "begin_boarding"

        if "begin boarding" in message_content: message_interpretation = "begin_boarding"
        if "begin the boarding" in message_content: message_interpretation = "begin_boarding"
        if "begin passenger boarding" in message_content: message_interpretation = "begin_boarding"

        if "start boarding" in message_content: message_interpretation = "begin_boarding"
        if "start the boarding" in message_content: message_interpretation = "begin_boarding"
        if "start passenger boarding" in message_content: message_interpretation = "begin_boarding"

        if "let passengers on" in message_content: message_interpretation = "begin_boarding"
        if "letting passengers on" in message_content: message_interpretation = "begin_boarding"

        # Profanity
        if "fuck" in message_content: message_interpretation = "profanity"
        if "shit" in message_content: message_interpretation = "profanity"
        if "bitch" in message_content: message_interpretation = "profanity"
        if "dick" in message_content: message_interpretation = "profanity"

    # Compile the response
    message_response = None

    random_will_do = random.choices([
        "Will do Captain, ",
        "Will do, ",
        "Understood - ",
        "No problem, ",
        "Sure, got it, "
    ])[0]

    random_will_report_back = random.choices([
        " We'll report back when we're done.",
        " I'll let you know when we're complete.",
        " I'll ping you when we're complete.",
        " I'll ping you when we're done.",
        ""
    ])[0]

    if message_interpretation == "pilot_wants_coffee":
        message_response = random.choices([
            "Coming right up!",
            "Just made a fresh pot, coming up."
        ])[0]

    if message_interpretation == "begin_boarding":

        message_response = random_will_do
        message_response = message_response + random.choices([
            "we'll begin boarding procedures now.",
            "letting them on now.",
            "we'll begin boarding now.",
            "boarding underway."
        ])[0]
        message_response = message_response + random_will_report_back

    if message_interpretation == "profanity":
        message_response = "Don't speak like that please."

    if message_response is None:
        message_response = random.choices([
            "I don't follow?",
            "Can you come again please?",
            "Didn't catch that, sorry",
            "Didn't catch that, sorry, come again please?",
            "Didn't get that, sorry, come again please?"
        ])[0]

    # Store and send the response
    if message_response is not None:
        create_new_message_from_crew(message_response, False)

        return jsonify({
            'status': 'success',
            'response': True,
            'message_response': message_response
        })


    return jsonify({
        'status': 'success',
        'response': False,
        'message_response': None
    })


def create_new_message_from_crew(message_content, read = False):

    # Create the response record
    new_message = FlightMessage(
        flight=current_user.active_flight_id,
        message_time=datetime.utcnow(),
        message_type="crew",
        message_from="crew",
        message_to="pilot",
        message_content=message_content,
        read=read  # Set as true because we're sending it
    )
    db.session.add(new_message)

    if not read:
        current_user.unread_flight_messages = current_user.unread_flight_messages + 1

    db.session.commit()

    return


