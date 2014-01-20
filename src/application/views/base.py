
import json

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
        return render_template('settings.html', **context)


class SubmitAlert(BaseView):

    def post(self):

        user = self.user
        sport_keyname = request.form['sport_keyname']

        Notification.create_notification(user, sport_keyname, kind='email')
        return json.dumps({'success': True})
