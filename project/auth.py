from flask import Blueprint, render_template, Flask, current_app, request, redirect, url_for
from flask_login import login_required, current_user
from . import db
from . import app
from datetime import datetime
from random import random, randint, randrange
import secrets
from .models import User
from sqlalchemy import desc
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == "GET":
        return render_template('auth/login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == "GET":
        return render_template('auth/register.html')

    # Check if passwords match
    if request.method == "POST":
        if request.form['password1'] != request.form['password2']:
            return render_template('auth/register.html', error_message="Passwords do not match")

    # Check if email is already registered
    existing_user = User.query.filter_by(email=request.form['email']).first()
    if existing_user:
        return render_template('auth/register.html', error_message="Email already registered")

    # Create unique setup key
    unique_setup_key = secrets.token_urlsafe(25)

    # If all ok then create the user
    new_user = User(
        email=request.form['email'],
        password=generate_password_hash(request.form['password1']),
        join_date=datetime.utcnow(),
        approved=True,
        unique_setup_key=unique_setup_key
    )

    db.session.add(new_user)
    db.session.commit()

    return render_template('auth/login.html', success_message="User created, please login")


@auth.route('/forgot_password')
def forgot():
    return "Not yet implemented"