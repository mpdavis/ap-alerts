"""
models.py

App Engine datastore models

"""
import hashlib
import random
import string

from google.appengine.ext import ndb

ALPHABET = string.ascii_lowercase + string.ascii_uppercase + string.digits


class User(ndb.Model):
    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty()
    salt = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now=True)

    ap_basketball_men_email = ndb.BooleanProperty(default=False)
    ap_basketball_women_email = ndb.BooleanProperty(default=False)

    def get_id(self):
        return self.key.id()

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_notifications(self):
        return Notification.query().filter(Notification.user == self.key).fetch()

    @classmethod
    def get_ap_bb_men_email(cls):
        return cls.query().filter(User.ap_basketball_men_email == True).fetch()

    @classmethod
    def get_by_email(cls, email):
        result = cls.query().filter(cls.email == email).fetch(1)
        if result:
            return result[0]
        return None

    @classmethod
    def generate_salt(cls, size=64):
        random.seed()
        return ''.join([random.choice(ALPHABET) for i in range(0, size)])

    @classmethod
    def encode_password(cls, raw_password, salt=None):

        if not salt:
            salt = cls.generate_salt()

        h = hashlib.new('sha512')
        h.update(raw_password)
        h.update(salt)

        return h.hexdigest(), salt

    @classmethod
    def check_password(cls, raw_password, email):
        user = cls.query().filter(cls.email == email).fetch(1)

        if len(user):
            user = user[0]
            response_hash, salt = cls.encode_password(raw_password, user.salt)
            return response_hash == user.password

        else:
            return False


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
