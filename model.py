from mongoengine import *
from pymongo import read_preferences
from ConfigParser import ConfigParser


class Arrival(Document):
    project = StringField(primary_key=True, unique=True)
    total = IntField(default=0)
    priority = DictField()
    severity = DictField()
    resolution = DictField()
    category = DictField()
    reporter = DictField()
    handler = DictField()
    status = DictField()
    date = DictField()
    week = DictField()
    month = DictField()

    meta = {"db_alias": "ticket"}


def initDB(config_file=None):
    config = ConfigParser()
    config.readfp(open(config_file or 'test.conf'))
    connect(config.get("MONGODB", "name"), alias="ticket", host=config.get("MONGODB", "url"), read_preference=read_preferences.ReadPreference.PRIMARY)


def toDate(dt):
    return dt.strftime("%Y%m%d")


def toWeek(dt):
    return dt.strftime("%YW%W")


def toMonth(dt):
    return dt.strftime("%Y%m")
