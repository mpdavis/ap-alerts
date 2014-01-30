"""
urls.py

URL dispatch route mappings and error handlers

"""
from flask import render_template

from application import app
from application import cron
from application.views import auth as auth_views
from application.views import base as base_views
from application.views import poll as poll_views


## URL dispatch rules
# App Engine warm up handler
# See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests
# app.add_url_rule('/_ah/warmup', 'warmup', view_func=views.warmup)

# Home page
app.add_url_rule('/', view_func=base_views.Index.as_view('index'))
app.add_url_rule('/register/', view_func=auth_views.Register.as_view('register'), methods=['GET', 'POST'])
app.add_url_rule('/login/', view_func=auth_views.Login.as_view('login'), methods=['GET', 'POST'])
app.add_url_rule('/logout/', view_func=auth_views.Logout.as_view('logout'))
app.add_url_rule('/settings/', view_func=base_views.Settings.as_view('settings'))

app.add_url_rule('/ajax/submit_alert', view_func=base_views.SubmitAlert.as_view('submit-alert'))
# app.add_url_rule('/ajax/submit_alerts', view_func=base_views.SubmitAlerts.as_view('submit-alerts'))

app.add_url_rule('/oauth/google_login', view_func=auth_views.GoogleLogin.as_view('google_login'))
app.add_url_rule('/oauth/google_authorized', view_func=auth_views.GoogleAuthorized.as_view('google_authorized'))

app.add_url_rule('/ap/basketball/men', view_func=poll_views.MenAPBasketball.as_view('ap-basketball-men'))
app.add_url_rule('/ap/basketball/women', view_func=poll_views.WomenAPBasketball.as_view('ap-basketball-women'))
app.add_url_rule('/coaches/basketball/men', view_func=poll_views.MenCoachesBasketball.as_view('coaches-basketball-men'))

app.add_url_rule('/test', view_func=base_views.Test.as_view('test'))

app.add_url_rule('/cron/ap/basketball/men', view_func=cron.MenAPBasketball.as_view('cron-ap-men-basketball'), methods=['GET'])
app.add_url_rule('/cron/coaches/basketball/men', view_func=cron.MenCoachesBasketball.as_view('cron-coaches-men-basketball'), methods=['GET'])
app.add_url_rule('/cron/ap/basketball/women', view_func=cron.WomenAPBasketball.as_view('cron-ap-women-basketball'), methods=['GET'])
# app.add_url_rule('/cron/test', view_func=cron.MenAPBasketball.as_view('cron-test'), methods=['GET'])


## Error handlers
# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Handle 500 errors
@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
