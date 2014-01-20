
import json

from flask import redirect
from flask import render_template
from flask import session
from flask import url_for

import flask_login
from flask_login import login_required

from flask_oauth import OAuth

from application.views import BaseView

from application.models import User

oauth = OAuth()

google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key="362610572777-94ond2hdlbklgtu38g1lkp6r8m6kb67t.apps.googleusercontent.com",
                          consumer_secret="fbeKtiCpCt1RbdGHpIDxSYEd")


def user_unauthorized_callback():
    return redirect(url_for('login'))


def load_user(userid):
    return User.get_by_id(int(userid))


class Register(BaseView):

    hide_nav = True

    def get(self):
        context = self.get_context()
        return render_template('register.html', **context)


class Login(BaseView):

    hide_nav = True

    def get(self):
        context = self.get_context()
        return render_template('login.html', **context)


class Logout(BaseView):
    decorators = [login_required]

    def get(self):
        flask_login.logout_user()
        return redirect(url_for('index'))


class GoogleLogin(BaseView):

    def get(self):
        callback = url_for('google_authorized', _external=True)
        return google.authorize(callback=callback)


class GoogleAuthorized(BaseView):

    @google.authorized_handler
    def get(self, other):

        # Setting the oauth token in the session
        session['oauth_token'] = str(self.get('access_token', ''))
        access_token = session['oauth_token']

        from urllib2 import Request, urlopen, URLError

        headers = {'Authorization': 'OAuth ' + access_token}
        req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                      None, headers)
        try:
            res = urlopen(req)

            if res:
                output = json.loads(res.read())
                if 'email' in output:
                    email = output['email']

                if email:
                    user = User.get_by_email(email)

                import logging
                logging.warn(user)

                if not user:
                    user = User(email=email)
                    user.put()

                if user:
                    flask_login.login_user(user)

        except URLError, e:
            if e.code == 401:
                # Unauthorized - bad token
                session.pop('access_token', None)
                return redirect(url_for('google_login'))
            return res.read()

        return redirect('/')


@google.tokengetter
def get_access_token():
    return session.get('access_token'), "fbeKtiCpCt1RbdGHpIDxSYEd"
