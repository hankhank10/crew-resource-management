from flask import Blueprint, render_template, Flask, current_app, request, redirect, url_for, flash
from flask_login import login_required, current_user, login_user, logout_user
from . import db
from . import app
from . import website_url
from datetime import datetime
from random import random, randint, randrange
import secrets
from .models import User, BetaSignupCode
from sqlalchemy import desc
from datetime import datetime
from project import inflight, email, auth


admin = Blueprint('admin', __name__)

@login_required
@admin.route('/admin/create_beta_code', methods=['GET', 'POST'])
def create_beta_code():

    if not current_user.is_superuser:
        return "Not authorised"

    if request.method == "POST":

        secret_key = secrets.token_hex(2) + "-" + secrets.token_hex(2) + "-" + secrets.token_hex(2)
        
        beta_code = BetaSignupCode(
            secret_key = secret_key,
            used = False
        )

        db.session.add(beta_code)
        db.session.commit()

        messages = []
        messages.append("Thank you for signing up for the <a href='https://crewmanager.live'>Crew Manager</a> Beta.")
        messages.append("Your signup has now been approved and you can now create an account using the beta code below.")
        messages.append("<h2>" + secret_key + "</h2>")
        messages.append("We look forward to seeing you in game")

        email.compose_and_send_message(
            request.form['email'], 
            "Crew Manager - Beta Signup Approved", 
            messages, 
            call_to_action_text = "Sign up now", 
            call_to_action_url = website_url + "/user/register"
        )

        flash ("Signup code sent", "success")
    
    return render_template('admin/create_beta_code.html')
