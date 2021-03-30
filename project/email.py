from project import secretstuff
from .models import BetaCode
from . import db

from envelopes import Envelope
import secrets

def send_message(to_address, subject, body):
    envelope = Envelope(
        from_addr=('admin@crewmanager.live', 'Crew Manager'),
        to_addr=(to_address, to_address),
        subject=subject,
        html_body=body
    )
    envelope.send(secretstuff.mail_smtp_server, login=secretstuff.mail_username, password=secretstuff.mail_password, tls=True)


def send_new_beta_code(to_address):

    secret_code = secrets.token_hex(10)

    new_beta_code = BetaCode(
        beta_code = secret_code,
        used = False
    )
    db.session.add(new_beta_code)
    db.session.commit()

    body_of_message = "<p>Thank you for applying for the Crew Manager Beta.</p>"
    body_of_message = body_of_message + "<p>You can now create an account using the beta access code: <b>" + secret_code + "</b></p>"
    body_of_message = body_of_message + '<p>Visit <a href="https://crewmanager.live/signup">Crew Manager</a> to sign up using this code</p>'

    send_message(to_address, "Crew Manager: Beta Invite", body_of_message)
    return secret_code


def send_verification_code(to_address):

    secret_code = secrets.token_hex(25)
    body_of_message = "<p>Thank you for creating an account with Crew Manager.</p>"
    body_of_message = body_of_message + '<p>Verify your account here <a href="https://crewmanager.live/user/verify/' + secret_code+ '">here</a></p>'

    send_message(to_address, "Crew Manager: Verify your email address", body_of_message)
    return secret_code