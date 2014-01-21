

from flask import render_template

from google.appengine.api import mail
from google.appengine.ext import deferred


def send_email(to_address, subject, body):

    sender = "Michael Davis <mike.philip.davis@gmail.com>"
    deferred.defer(mail.send_mail, sender=sender, to=to_address, subject=subject, body=body)


def generate_body(template, context=None, **kwargs):

    ctx = {}
    if context:
        ctx.update(context)
    ctx.update(kwargs)

    return render_template(template, **ctx)


def send_emails(notifications):

    body = generate_body('notifications/email/alert.html')

    for notification in notifications:
        send_email(notification.user.get().email, 'New Poll Alert', body)


def welcome_user(email):
    
