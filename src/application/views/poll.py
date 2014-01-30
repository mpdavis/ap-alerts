

from flask import abort
from flask import render_template

from application.views import BaseView

from application.models import Ranking, Week, Poll


class PollView(BaseView):

    keyname = None
    template = None

    def get(self):
        context = self.get_context()

        poll = Poll.get_or_insert(self.keyname)
        weeks = Week.query().filter(Week.poll == poll.key).order(-Week.week).fetch()

        if not weeks:
            abort(500)

        rankings = Ranking.query().filter(Ranking.week == weeks[0].key).order(Ranking.rank).fetch()

        context['sport_keyname'] = self.keyname
        context['weeks'] = weeks
        context['week_rankings'] = rankings

        return render_template(self.template, **context)


class MenAPBasketball(PollView):
    keyname = 'college:ap:basketball:men:2013'
    template = 'polls/ap/men/basketball.html'


class MenCoachesBasketball(PollView):
    keyname = 'college:coaches:basketball:men:2013'
    template = 'polls/coaches/men/basketball.html'


class WomenAPBasketball(PollView):
    keyname = 'college:ap:basketball:women:2013'
    template = 'polls/ap/women/basketball.html'
