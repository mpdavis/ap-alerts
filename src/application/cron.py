
import logging

from bs4 import BeautifulSoup

from google.appengine.api import urlfetch

from models import Ranking, Sport, Team, Week, User, Poll

from application.notifications import email


def check_basketball_coaches_poll():
    url = "http://www.usatoday.com/sports/ncaab/polls/"

    response = urlfetch.fetch(url)

    poll = Poll.get_or_insert(
        'college:coaches:basketball:men:2013_2014',
        poll='coaches',
        sport='basketball',
        gender='men',
        year='2013_2014'
    )

    soup = BeautifulSoup(response.content)

    week = Week.query().filter(Week.poll == poll.key).filter(Week.week == '13').fetch()

    if week:
        logging.debug('No new info found for college:basketball:women:2013')
        return ''
    else:
        week = Week(poll=poll.key, week='13')
        week.put()

    rankings = []

    # table = soup('table', class_='poll')
    for tr in soup('tr'):
        ranking_tds = tr.find_all('td', class_='ranking')
        if ranking_tds:
            rank = tr('td', class_='ranking')[0].text.strip()
            record = tr('td', class_='record')[0].text.strip()
            first_name = tr('span', class_='first_name')[0].text.strip()
            last_name = tr('span', class_='last_name')[0].text.strip()
            team = '%s %s' % (first_name, last_name)
            previous = tr('td', class_='ranking_previous')[0].text.strip()

            team_entity = Team.get_or_insert(team, name=team)
            ranking = Ranking(team=team_entity.key, week=week.key, rank=int(rank), record=record, previous=previous)
            ranking.put()
            rankings.append(ranking)

    users = User.get_coaches_bb_men_email()
    email.send_alert(users, rankings, "USA Today Coaches Poll - Men's Basketball")

    return response.content


def check_basketball_ap_womens():
    url = "http://espn.go.com/womens-college-basketball/rankings/_/poll/1/week/13/"
    response = urlfetch.fetch(url)
    poll = Poll.get_or_insert(
        'college:basketball:women:2013',
        poll='ap',
        sport='basketball',
        gender='women',
        year='2013',
    )

    soup = BeautifulSoup(response.content)

    week = Week.query().filter(Week.poll == poll.key).filter(Week.week == '13').fetch()

    if week:
        logging.debug('No new info found for college:basketball:women:2013')
    else:
        week = Week(poll=poll.key, week='13')
        week.put()

    rankings = []




def check_basketball_ap_poll():

    ap_url = "http://collegebasketball.ap.org/poll"

    response = urlfetch.fetch(ap_url)

    if not response.status_code == 200:
        return "ERROR"

    sport = Sport.get_or_insert('college:basketball:men:2013_2014',
                                sport='basketball',
                                gender='men',
                                year='2013_2014')

    soup = BeautifulSoup(response.content)

    # Find current week
    all_h2 = soup('h2', class_='block-title')
    for h2 in all_h2:
        if h2.text.lower().startswith('week'):
            this_week = h2.text.split(' ')[1]

    week = Week.query().filter(Week.sport == sport.key).filter(Week.week == this_week).fetch()

    if week:
        logging.debug("No new info.")
        return ''
    else:
        week = Week(sport=sport.key, week=this_week)
        week.put()
        logging.warn("New week. Lets get to scraping.")

    rankings = []

    # Parse rank info from the page
    for tag in soup('tr'):

        rank = tag(class_='trank')
        if not len(rank) == 1:
            logging.error('Parsing rank from AP table error.')
        rank = int(rank[0].text)

        all_links = tag('a')
        if not len(all_links) == 2:
            logging.error('Error parsing links from AP table.')
        team = all_links[0].text
        conference = all_links[1].text

        record = tag(class_='poll-record')[0].text.split(' ')[1]

        team_key = '%s:%s' % (team, conference)
        team_entity = Team.get_or_insert(team_key, name=team, conference=conference)
        ranking = Ranking(team=team_entity.key, week=week.key, rank=rank, record=record)
        ranking.put()
        rankings.append(ranking)

    users = User.get_ap_bb_men_email()
    email.send_alert(users, rankings, "AP Men's Basketball")

    return response.content
