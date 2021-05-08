from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.sql.expression import false


# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

#def create_app():
app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crew-resource-management-db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# Set the main URL
website_url = "https://sopwith.crewmanager.live"



# db init
from .models import User, Flight, EquipmentType, BetaSignupCode, FlightMessage

db.init_app(app)
migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# blueprints
from .main import main as main_blueprint
app.register_blueprint(main_blueprint)

from .auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

from .custom_admin import custom_admin as custom_admin_blueprint
app.register_blueprint(custom_admin_blueprint)

from .flight_manager import flight_manager as flight_manager_blueprint
app.register_blueprint(flight_manager_blueprint)

from .api_airport_lookup import api_airport_lookup as api_airport_lookup_blueprint
app.register_blueprint(api_airport_lookup_blueprint)

from .equipment import equipment as equipment_blueprint
app.register_blueprint(equipment_blueprint)

from .inflight import inflight as inflight_blueprint
app.register_blueprint(inflight_blueprint)

from .messaging import messaging as messaging_blueprint
app.register_blueprint(messaging_blueprint)

from .passengers import passengers as passengers_blueprint
app.register_blueprint(passengers_blueprint)

from .crew import crew as crew_blueprint
app.register_blueprint(crew_blueprint)

from .cron import cron as cron_blueprint
app.register_blueprint(cron_blueprint)


# Flask admin

# Create customized model view class
class MyModelView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.is_superuser
        return false


admin = Admin(app, name='Crew Manager Admin', template_mode='bootstrap3')

admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Flight, db.session))
admin.add_view(MyModelView(EquipmentType, db.session))
admin.add_view(MyModelView(BetaSignupCode, db.session))
admin.add_view(MyModelView(FlightMessage, db.session))






