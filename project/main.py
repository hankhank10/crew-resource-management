from flask import Blueprint, render_template, Flask, current_app
from flask_login import login_required, current_user
from . import db
from . import app



main = Blueprint('main', __name__)

@main.route('/')
@login_required
def dashboard():

    return render_template('index.html')