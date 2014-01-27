

from flask import flash
from flask import render_template

from application.views import BaseView

from application.models import Ranking, Week


class MensBasketball(BaseView):

    def get(self):
        context = self.get_context()

        context['sport_keyname'] = 'college:basketball:men:2013_2014'
        context['weeks'] = Week.query().order(-Week.week).fetch()
        context['week_rankings'] = Ranking.query().filter(Ranking.week == context['weeks'][0].key).order(Ranking.rank).fetch()
        return render_template('polls/ap/men/basketball.html', **context)


class CoachesBasketballMen(BaseView):

    def get(self):
        context = self.get_context()

        context['sport_keyname'] = 'college:coaches:basketball:men:2013_2014'
        context['weeks'] = Week.query().order(-Week.week).fetch()
        context['week_rankings'] = Ranking.query().filter(Ranking.week == context['weeks'][0].key).order(Ranking.rank).fetch()
        return render_template('polls/coaches/men/basketball.html', **context)