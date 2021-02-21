from flask import Blueprint, render_template, Flask, current_app
from flask_login import login_required, current_user
from . import db
from . import app
import time
from random import random, randint, randrange
import secrets
from .models import User
from sqlalchemy import desc
from datetime import datetime


main = Blueprint('main', __name__)

@main.route('/')
def index():

    return "Hello world"