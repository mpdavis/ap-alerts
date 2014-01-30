
import logging

from bs4 import BeautifulSoup

from google.appengine.api import urlfetch

from models import Ranking, Team, Week, User, Poll

from application.notifications import email
from application.views import BaseView


class PollCronView(BaseView):

    url = None
    level = None
    poll = None
    sport = None
    gender = None
    year = None
    email_subject = None

    def create_poll_key(self):
        return '%s:%s:%s:%s:%s' % (self.level, self.poll, self.sport, self.gender, self.year)

    def get_poll(self):
        poll = Poll.get_or_insert(
            self.create_poll_key(),
            level=self.level,
            poll=self.poll,
            sport=self.sport,
            gender=self.gender,
            year=self.year,
        )

        return poll

    def get_previous_week(self):
        week = Week.query().filter(Week.poll == self.get_poll().key).order(-Week.week).fetch(1)
        if not week:
            return '-1'
        return week[0].week

    def parse_current_week(self, soup):
        pass

    def parse_team_info(self, soup):
        pass

    def get_users(self):
        pass

    def get(self):
        response = urlfetch.fetch(self.url)

        soup = BeautifulSoup(response.content)

        old_week = self.get_previous_week()
        current_week = self.parse_current_week(soup)

        if old_week == current_week:
            logging.debug('No new info for %s' % self.create_poll_key())
            return ''

        poll = self.get_poll()
        logging.warn(current_week)
        week = Week(poll=poll.key, week=current_week)
        week.put()

        team_info = self.parse_team_info(soup)

        rankings = []
        for info in team_info:
            team_entity = Team.get_or_insert(info['name'], name=info['name'])
            ranking = Ranking(
                team=team_entity.key,
                week=week.key,
                rank=int(info['rank']),
                record=info['record'],
                previous=info['previous']
            )
            ranking.put()
            rankings.append(ranking)

        users = self.get_users()
        if users:
            email.send_alert(users, rankings, self.email_subject)

        return response.content


class WomenAPBasketball(PollCronView):

    url = "http://espn.go.com/womens-college-basketball/rankings/_/poll/1/week/13/"
    level = 'college'
    poll = 'ap'
    sport = 'basketball'
    gender = 'women'
    year = '2013'
    email_subject = "Women's AP Poll"

    def parse_current_week(self, soup):
        return '13'

    def parse_team_info(self, soup):
        info = []
        rank = 1

        teams = soup.find_all('ul', class_='team-summary')
        for row in teams:
            team = row.find_all('a')[0].text
            record = row('li', class_='record')[0].text
            previous = row('span', class_='prev-rank')[0].text

            team_info = {
                'rank': rank,
                'name': team,
                'record': record,
                'previous': previous,
            }

            info.append(team_info)

            rank += 1

        return info

    def get_users(self):
        return User.get_ap_bb_women_email()


class MenAPBasketball(PollCronView):

    url = "http://collegebasketball.ap.org/poll"
    level = 'college'
    poll = 'ap'
    sport = 'basketball'
    gender = 'men'
    year = '2013'
    email_subject = "Men's AP Poll"

    def parse_current_week(self, soup):
        all_h2 = soup('h2', class_='block-title')
        for h2 in all_h2:
            if h2.text.lower().startswith('week'):
                this_week = h2.text.split(' ')[1]
        return this_week

    def get_users(self):
        return User.get_ap_bb_men_email()

    def parse_team_info(self, soup):
        info = []

        for tag in soup('tr'):

            rank = tag(class_='trank')
            if not len(rank) == 1:
                logging.error('Parsing rank from AP table error.')
            rank = int(rank[0].text)

            all_links = tag('a')
            if not len(all_links) == 2:
                logging.error('Error parsing links from AP table.')
            team = all_links[0].text

            record = tag(class_='poll-record')[0].text.split(' ')[1]

            info.append({
                'rank': rank,
                'name': team,
                'record': record,
                'previous': ''
            })

        return info


class MenCoachesBasketball(PollCronView):

    url = "http://www.usatoday.com/sports/ncaab/polls/"
    level = 'college'
    poll = 'coaches'
    sport = 'basketball'
    gender = 'men'
    year = '2013'
    email_subject = "Men's USA Today Coaches Poll"

    def parse_current_week(self, soup):
        return '13'

    def get_users(self):
        return User.get_coaches_bb_men_email()

    def parse_team_info(self, soup):
        info = []

        for tr in soup('tr'):
            ranking_tds = tr.find_all('td', class_='ranking')
            if ranking_tds:
                rank = tr('td', class_='ranking')[0].text.strip()
                record = tr('td', class_='record')[0].text.strip()
                team = tr('span', class_='first_name')[0].text.strip()
                previous = tr('td', class_='ranking_previous')[0].text.strip()

                info.append({
                    'rank': rank,
                    'name': team,
                    'record': record,
                    'previous': previous
                })

        return info
