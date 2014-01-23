"""
forms.py

Web forms based on Flask-WTForms

See: http://flask.pocoo.org/docs/patterns/wtforms/
     http://wtforms.simplecodes.com/

"""

import wtforms
from wtforms import validators


class RegisterForm(wtforms.Form):
    email = wtforms.TextField('Email', validators=[validators.Email(), validators.Required()])
    password = wtforms.TextField('Password', validators=[validators.Required()])
    confirm_password = wtforms.TextField('Confirm Password', validators=[validators.Required()])


class LoginForm(wtforms.Form):
    email = wtforms.TextField('Email', validators=[validators.Email(), validators.Required()])
    password = wtforms.TextField('Password', [validators.Required()])
