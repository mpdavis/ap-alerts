
import flask_login

from flask.views import MethodView
from flask import session


class BaseView(MethodView):

    hide_nav = False

    @property
    def session(self):
        return session

    @property
    def user(self):
        if not flask_login.current_user.is_anonymous():
            return flask_login.current_user._get_current_object()
        else:
            return None

    def get_context(self, extra_ctx=None, **kwargs):

        ctx = {
            'user': self.user,
            'hide_nav': self.hide_nav,
        }
        if extra_ctx:
            ctx.update(extra_ctx)
        ctx.update(kwargs)
        return ctx
