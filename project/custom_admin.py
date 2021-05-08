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
import coolname


custom_admin = Blueprint('custom_admin', __name__)


@login_required
@custom_admin.route('/admin/create_beta_code', methods=['GET', 'POST'])
def create_beta_code():

    if not current_user.is_superuser:
        return "Not authorised"

    if request.method == "POST":

        secret_key = coolname.generate_slug(3)
        
        beta_code = BetaSignupCode(
            secret_key = secret_key,
            used = False,
            email_sent_to = request.form['email']
        )

        db.session.add(beta_code)
        db.session.commit()

        messages = []
        messages.append("Thank you for volunteering to be a beta tester for <a href='https://crewmanager.live'>Crew Manager</a>.")
        messages.append("I am now opening the app for very, very early beta testing for a handful of testers to get some feedback and identify obvious bugs. You should be aware that this is very much early software, not everything is functional and you 100% will experience bugs. I also plan to release new versions pretty regularly so there's a very good chance that your data will get deleted at some point.")
        messages.append("You can see the <a href='https://forum.crewmanager.live/d/4-dev-diary-2-feature-roadmap'>features that are up and running, and what is not yet, at the forum</a>.")
        messages.append("If early stage testing is not your thing, then that's fine - send me an email and I'll keep you on the list for more polished versions.")
        messages.append("If you are willing to dive into the bleeding edge then we'd love to have you on board. The one thing I do ask is that you report bugs as you find them. The best way to do this is by clicking the little blue 'Feedback' button at the bottom right of each page. Or if you know what you're doing then please feel free to raise an issue on <a href='https://github.com/hankhank10/crew-resource-management'>GitHub</a> (or even better dive into the open source code and fix it yourself!)")
        messages.append("The beta version is running at <a href='http://sopwith.crewmanager.live'>http://sopwith.crewmanager.live</a> - you can create an account using the beta signup code below. This is unique to you.")
        messages.append("<h2>" + secret_key + "</h2>")
        messages.append("We look forward to seeing you in game - please do also <a href='https://discord.gg/NqPEKnWCF8'>join the discord</a> and <a href='https://forum.crewmanager.live/'>visit the forum</a>.")

        email.compose_and_send_message(
            request.form['email'], 
            "Crew Manager - Beta Signup Approved", 
            messages, 
            call_to_action_text = "Sign up now", 
            call_to_action_url = website_url + "/user/register-with-code/" + secret_key
        )

        flash("Signup code sent to " + request.form['email'], "success")
    
    return render_template('admin/create_beta_code.html')
