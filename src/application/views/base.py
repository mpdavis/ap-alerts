

import json
import logging

from flask import render_template
from flask import request

from flask_login import login_required

from application.views import BaseView

from application.models import Notification


class Index(BaseView):

    def get(self):
        context = self.get_context()
        return render_template('index.html', **context)


class Settings(BaseView):
    decorators = [login_required]

    def get(self):
        context = self.get_context()

        context['ap_basketball_men_email'] = self.user.ap_basketball_men_email

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
        sport_keyname = request.form['sport_keyname']

        Notification.create_notification(user, sport_keyname, kind='email')
        return json.dumps({'success': True})
