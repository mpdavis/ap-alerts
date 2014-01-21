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
app.add_url_rule('/register/', view_func=auth_views.Register.as_view('register'))
app.add_url_rule('/login/', view_func=auth_views.Login.as_view('login'))
app.add_url_rule('/logout/', view_func=auth_views.Logout.as_view('logout'))
app.add_url_rule('/settings/', view_func=base_views.Settings.as_view('settings'))

app.add_url_rule('/ajax/submit_alert', view_func=base_views.SubmitAlert.as_view('submit-alert'))
# app.add_url_rule('/ajax/submit_alerts', view_func=base_views.SubmitAlerts.as_view('submit-alerts'))

app.add_url_rule('/oauth/google_login', view_func=auth_views.GoogleLogin.as_view('google_login'))
app.add_url_rule('/oauth/google_authorized', view_func=auth_views.GoogleAuthorized.as_view('google_authorized'))

app.add_url_rule('/ap/basketball/men', view_func=poll_views.MensBasketball.as_view('ap-basketball-men'))

# # Say hello
# app.add_url_rule('/hello/<username>', 'say_hello', view_func=views.say_hello)

# # Examples list page
# app.add_url_rule('/examples', 'list_examples', view_func=views.list_examples, methods=['GET', 'POST'])

# # Examples list page (cached)
# app.add_url_rule('/examples/cached', 'cached_examples', view_func=views.cached_examples, methods=['GET'])

# # Contrived admin-only view example
# app.add_url_rule('/admin_only', 'admin_only', view_func=views.admin_only)

# # Edit an example
# app.add_url_rule('/examples/<int:example_id>/edit', 'edit_example', view_func=views.edit_example, methods=['GET', 'POST'])

# # Delete an example
# app.add_url_rule('/examples/<int:example_id>/delete', view_func=views.delete_example, methods=['POST'])

app.add_url_rule('/cron/check_basketball', view_func=cron.check_basketball_ap_poll, methods=['GET'])


## Error handlers
# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Handle 500 errors
@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
