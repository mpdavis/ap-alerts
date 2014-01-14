"""
models.py

App Engine datastore models

"""


from google.appengine.ext import ndb


class Team(ndb.Model):
    name = ndb.StringProperty(required=True)
    conference = ndb.StringProperty(required=False)


class Sport(ndb.Model):
    sport = ndb.StringProperty(required=True)
    gender = ndb.StringProperty(required=True)
    year = ndb.StringProperty(required=True)


class Week(ndb.Model):
    week = ndb.StringProperty(required=True)
    sport = ndb.KeyProperty(kind=Sport)


class Ranking(ndb.Model):
    rank = ndb.IntegerProperty(required=True)
    team = ndb.KeyProperty(kind=Team)
    week = ndb.KeyProperty(kind=Week)
    record = ndb.StringProperty()
