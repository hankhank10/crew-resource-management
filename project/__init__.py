from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate


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

# db init
from .models import User

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

###  ADMIN 
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
#from .admin import AdminView

#app.config['FLASK_ADMIN_SWATCH'] = 'cosmo'

#admin = Admin(app, name='Admin', index_view=AdminView(User, db.session, url='/admin', endpoint='admin'))
#admin.add_view(AdminView(Message, db.session))





