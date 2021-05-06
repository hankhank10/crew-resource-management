from flask import Blueprint, render_template, Flask, current_app, request, redirect, url_for, flash
from flask_login import login_required, current_user, login_user, logout_user
from . import db
from . import app
from datetime import datetime
from random import random, randint, randrange
import secrets
from .models import User, BetaSignupCode
from sqlalchemy import desc
from datetime import datetime
from project import inflight, email

from werkzeug.security import generate_password_hash, check_password_hash


auth = Blueprint('auth', __name__)


@auth.route('/user/login', methods=['GET', 'POST'])
def login():

    if request.method == "GET":
        return render_template('auth/login.html')

    if request.method == "POST":

        # Check if username and password are found
        user = User.query.filter_by(email=request.form['email']).first()

        if not user or not check_password_hash(user.password, request.form['password']):
            flash('Please check your login details and try again.', 'danger')
            return render_template('auth/login.html')

        if user.verified == False:
            flash('Email address not verified - another authorisation code sent to your email', 'danger')
            user.unique_setup_key = email.send_verification_code(user.email)
            db.session.commit()
            return render_template('auth/login.html')

        if user.approved == False:
            flash('Thank you for signing up to the beta - we will notify you when your account is available', 'danger')
            return render_template('auth/login.html')

        login_user(user, remember=True)

        return redirect(url_for('main.dashboard'))


@auth.route('/user/register', methods=['GET', 'POST'])
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

    # Check if beta signup code is value
    beta_code = BetaSignupCode.query.filter_by(secret_key = request.form['beta_code']).first()
    
    if not beta_code:
        flash ("Beta code invalid", "danger")
        return render_template('auth/register.html')

    if beta_code.used:
        flash ("Beta code already used", "danger")
        return render_template('auth/register.html')

    beta_code.used = True

    # Create unique setup key
    unique_setup_key = email.send_verification_code(request.form['email'])

    # If all ok then create the user
    new_user = User(
        email=request.form['email'],
        name=request.form['name'],
        password=generate_password_hash(request.form['password1']),
        join_date=datetime.utcnow(),
        approved=False,
        verified=False,
        unique_setup_key=unique_setup_key
    )

    db.session.add(new_user)
    db.session.commit()

    flash ("Account created - please visit your email to verify your account", "success")
    return redirect(url_for('auth.login'))


@auth.route('/user/verify/<unique_setup_key>',)
def verify(unique_setup_key):
    existing_user = User.query.filter_by(unique_setup_key=unique_setup_key).first_or_404()

    existing_user.verified = True
    existing_user.unique_setup_key = None
    db.session.commit()

    flash ("Thank you for verifying your email address", "success")
    return redirect(url_for('auth.login'))


@auth.route('/user/logout')
@login_required
def logout():
    logout_user()
    flash ("Logged out", "danger")
    return redirect(url_for('auth.login'))


@auth.route('/user/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == "GET":
        return render_template('/auth/change_password.html', error_message=None)

    if request.method == "POST":
        # check passwords match
        if request.form['new_password1'] != request.form['new_password2']:
            return render_template('/auth/change_password.html', error_message="Passwords must match")

        if len(request.form['new_password1']) < 5:
            return render_template('/auth/change_password.html', error_message="Password too short")

        # check current password
        if check_password_hash(current_user.password, request.form['old_password']):

            current_user.password = generate_password_hash(request.form['new_password1'])
            db.session.commit()

            flash("Password updated successfully", "success")
            return redirect(url_for('inflight.dashboard'))

        else:
            return render_template('/auth/change_password.html', error_message="Existing password incorrect")


@auth.route('/user/forgot_password')
def forgot():
    return "Not yet implemented"