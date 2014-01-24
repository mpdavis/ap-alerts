

import json
import logging

from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

import flask_login
from flask_login import login_required

from flask_oauth import OAuth

from application.forms import LoginForm
from application.forms import RegisterForm
from application.views import BaseView
from application.models import User
from application.notifications.email import welcome_user

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
        context['form'] = RegisterForm()
        return render_template('register.html', **context)

    def post(self):
        form = RegisterForm(request.form)
        registered = False
        error = ''
        if form.validate():

            password, salt = User.encode_password(form.password.data)

            current_user = User.get_by_email(form.email.data)
            if current_user:
                return json.dumps({'registered': False, 'error_message': 'current_user'})

            new_user = User(email=form.email.data, password=password, salt=salt)
            new_user.put()
            welcome_user(new_user)
            registered = True

            flask_login.login_user(new_user)

        if form.errors:

            email_errors = form.errors.get('email', None)
            password_errors = form.errors.get('password', None)

            if email_errors:
                logging.warn(email_errors)
                if 'Invalid email address.' in email_errors:
                    error = "invalid_email"

            if password_errors:
                if 'Field must be at least 5 characters long.' in password_errors:
                    error = 'password_length'

        return json.dumps({'registered': registered, 'error_message': error})


class Login(BaseView):

    hide_nav = True

    def get(self):
        context = self.get_context()
        context['form'] = LoginForm()
        return render_template('login.html', **context)

    def post(self):
        form = LoginForm(request.form)
        authorized = False
        message = ''

        if form.validate():
            authorized = User.check_password(form.password.data, form.email.data)

            if not authorized:
                message = "incorrect_password"
            else:
                user = User.get_by_email(form.email.data)
                flask_login.login_user(user)
        else:
            message = "no_user"

        response = json.dumps({
            'authorized': authorized,
            'error_message': message
        })

        return response


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

                if not user:
                    user = User(email=email)
                    user.put()
                    welcome_user(user)

                if user:
                    flask_login.login_user(user)

        except URLError, e:
            if e.code == 401:
                # Unauthorized - bad token
                session.pop('access_token', None)
                return redirect(url_for('google_login'))
            return res.read()

        return redirect(url_for('settings'))


@google.tokengetter
def get_access_token():
    return session.get('access_token'), "fbeKtiCpCt1RbdGHpIDxSYEd"
