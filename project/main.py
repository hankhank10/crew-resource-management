from flask import Blueprint, render_template, Flask, current_app, redirect
from flask_login import login_required, current_user
from . import db
from . import app
from project import crew, passengers, email
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


main = Blueprint('main', __name__)


@main.route('/')
@login_required
def dashboard():

    return render_template('index.html')


@main.route('/backend/setup')
def backend_setup():
    passengers.create_new_passengers(10000)
    crew.create_new_crew_members(1000)

    new_user = User(
        email='admin@findmyplane.live',
        name='Admin',
        password=generate_password_hash('password'),
        join_date=datetime.utcnow(),
        verified=True,
        approved=True,
        unique_setup_key='not necessary',
        is_superuser=True
    )
    db.session.add(new_user)
    db.session.commit()

    return "OK!"


@login_required
@main.route('/download/client')
def download_client():

    current_user.tutorial_downloaded_client = True
    db.session.commit()

    return redirect("https://findmyplane.live/download/findmyplane-setup.zip")
