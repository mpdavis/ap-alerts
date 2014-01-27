
import json
import logging

from flask import render_template

from google.appengine.api import mail
from google.appengine.api import urlfetch
from google.appengine.ext import deferred


# def send_email(to_address, subject, body):

#     sender = "PollAlerts <mike.philip.davis@gmail.com>"
#     deferred.defer(mail.send_mail, sender=sender, to=to_address, subject=subject, body=body)


def generate_body(template, context=None, **kwargs):

    ctx = {}
    if context:
        ctx.update(context)
    ctx.update(kwargs)

    return render_template(template, **ctx)


def send_alert(users, rankings, subject):

    body = generate_body('notifications/email/alert.html', rankings=rankings, title=subject)
    subject = "New PollAlert - %s" % subject
    send_email(users, subject, body)


def welcome_user(user):
    body = generate_body('notifications/email/welcome.html')
    subject = "Welcome to PollAlerts"
    send_email(user, subject, body)


def send_email(users, subject, html, from_email="no-reply@pollalerts.com", from_name="PollAlerts"):

    if not isinstance(users, list):
        users = [users]

    to_addresses = []
    for user in users:
        to_addresses.append({"email": user.email, 'type': 'to'})

    payload = {
        "key": "0F0tSWKOJExYgekt_IhCGg",
        "message": {
            "html":                 html,
            "subject":              subject,
            "from_email":           from_email,
            "from_name":            from_name,
            "track_clicks":         False,
            "preserve_recipients":  False,
            "to":                   to_addresses,
            "bcc_address":          "mike.philip.davis@gmail.com",
        }
    }

    content = urlfetch.fetch(
        "https://mandrillapp.com/api/1.0/messages/send.json",
        method=urlfetch.POST,
        headers={'Content-Type': 'application/json'},
        payload=json.dumps(payload)
    )

    logging.debug(content.content)
