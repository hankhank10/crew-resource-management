from flask import Blueprint, render_template, Flask, current_app, request, redirect, url_for, flash
from flask_login import login_required, current_user, login_user, logout_user
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

    if request.method == "POST":

        # Check if username and password are found
        user = User.query.filter_by(email=request.form['email']).first()

        if not user or not check_password_hash(user.password, request.form['password']):
            flash('Please check your login details and try again.', 'danger')
            return render_template('auth/login.html')

        login_user(user, remember=True)

        return redirect(url_for('main.dashboard'))


@auth.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == "GET":
        return render_template('auth/register.html')

    # Check if passwords match
    if request.method == "POST":
        if request.form['password1'] != request.form['password2']:
            flash ("Passwords do not match", "danger")
            return render_template('auth/register.html')

    # Check if email is already registered
    existing_user = User.query.filter_by(email=request.form['email']).first()
    if existing_user:
        flash ("Email already registered", "danger")
        return render_template('auth/register.html')

    # Create unique setup key
    unique_setup_key = secrets.token_urlsafe(25)

    # If all ok then create the user
    new_user = User(
        email=request.form['email'],
        name=request.form['name'],
        password=generate_password_hash(request.form['password1']),
        join_date=datetime.utcnow(),
        approved=True,
        unique_setup_key=unique_setup_key
    )

    db.session.add(new_user)
    db.session.commit()

    flash ("User created, please login", "success")
    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash ("Logged out", "danger")
    return redirect(url_for('auth.login'))


@auth.route('/forgot_password')
def forgot():
    return "Not yet implemented"