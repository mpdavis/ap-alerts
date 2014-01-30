

import json
import logging

from flask import render_template
from flask import request

from flask_login import login_required

from application.views import BaseView


class Test(BaseView):

    def get(self):
        from application.notifications import email
        from application.models import User
        user = User.get_ap_bb_men_email()
        logging.warn(user)
        email.send_emails(user)
        return 'Test'


class Index(BaseView):

    def get(self):
        context = self.get_context()
        return render_template('index.html', **context)


class Settings(BaseView):
    decorators = [login_required]

    def get(self):
        context = self.get_context()

        context['ap_basketball_men_email'] = self.user.ap_basketball_men_email
        context['ap_basketball_women_email'] = self.user.ap_basketball_women_email
        context['coaches_basketball_men_email'] = self.user.coaches_basketball_men_email

        return render_template('settings.html', **context)

    def post(self):
        for alert in request.form:
            if hasattr(self.user, alert):
                value = True if request.form[alert] == 'true' else False
                setattr(self.user, alert, value)

        self.user.put()

        return json.dumps({'success': True})


class SubmitAlert(BaseView):

    def post(self):

        user = self.user
        alert_name = request.form['alert_name']
        if hasattr(user, alert_name):
            setattr(user, alert_name, True)

        user.put()

        return json.dumps({'success': True})
