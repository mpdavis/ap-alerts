
import logging

from bs4 import BeautifulSoup

from google.appengine.api import urlfetch

from models import Ranking, Sport, Team, Week, Notification


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
    logging.warn(all_h2)
    for h2 in all_h2:
        if h2.text.lower().startswith('week'):
            this_week = h2.text.split(' ')[1]

    week = Week.query().filter(Week.sport == sport.key).filter(Week.week == this_week).fetch()

    if week:
        logging.warn("WEEK found, already seen it.")
        return ''
    else:
        week = Week(sport=sport.key, week=this_week)
        week.put()
        logging.warn("WEEK not found, new info!")

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

    notifications = Notification.get_notifications(sport)
    from application.notifications import email
    email.send_emails(notifications)

    return response.content
