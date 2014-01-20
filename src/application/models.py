"""
models.py

App Engine datastore models

"""


from google.appengine.ext import ndb


class User(ndb.Model):
    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty()
    salt = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now=True)

    def get_id(self):
        return self.key.id()

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_notifications(self):
        return Notification.query().filter(Notification.email == self.email).fetch()

    @classmethod
    def get_by_email(cls, email):
        result = cls.query().filter(cls.email == email).fetch(1)
        if result:
            return result[0]
        return None


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


class Notification(ndb.Model):
    user = ndb.KeyProperty(kind=User)
    sport = ndb.KeyProperty(kind=Sport)
    kind = ndb.StringProperty()

    @classmethod
    def get_notifications(cls, sport):
        result = Notification.query().filter(Notification.sport == sport.key).fetch()
        return result

    @classmethod
    def create_notification(cls, user, sport_keyname, kind='email'):
        sport = ndb.Key(Sport, 'college:basketball:men:2013_2014').get()
        result = Notification.query().filter(Notification.user == user.key).filter(Notification.sport == sport.key).fetch()
        if result:
            return result[0]

        notification = Notification(user=user.key, sport=sport.key, kind=kind)
        notification.put()
        return notification
