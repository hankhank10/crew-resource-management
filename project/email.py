from flask.templating import render_template
from project import secretstuff
from . import db
from . import website_url

from envelopes import Envelope
import secrets


def compose_message(messages, call_to_action_text = None, call_to_action_url = None):

    return render_template(
        '/email/email-base.html', 
        messages = messages, 
        call_to_action_url = call_to_action_url, 
        call_to_action_text = call_to_action_text
    )


def send_message(to_address, subject, body):
    envelope = Envelope(
        from_addr=('admin@crewmanager.live', 'Crew Manager for MSFS 2020'),
        to_addr=(to_address, to_address),
        subject=subject,
        html_body=body
    )
    envelope.send(secretstuff.mail_smtp_server, login=secretstuff.mail_username, password=secretstuff.mail_password, tls=True)


def compose_and_send_message(to_address, subject, messages, call_to_action_text = None, call_to_action_url = None):

    html_body = compose_message(messages, call_to_action_text, call_to_action_url)
    send_message(to_address, subject, html_body)


def send_verification_code(to_address):

    secret_code = secrets.token_hex(15)

    body_of_message = []
    body_of_message.append("Thank you for creating an account with <a href='"+ website_url + "'>Crew Manager</a>.")
    body_of_message.append("Before you can use your account you must verify your email address by clicking the link below.")

    call_to_action_text = "Verify your account"
    call_to_action_url = website_url + "/user/verify/" + secret_code

    compose_and_send_message(to_address, "Crew Manager: Verify your email address", body_of_message, call_to_action_text, call_to_action_url)

    return secret_code
