from datetime import datetime

from dbdiff.fixture import Fixture

from django import test

from freezegun import freeze_time

import pytz

from posts.models import Stat, Post

from .management.commands.twitter_stream import Command as TwitterStream


class TestTwitterStream(test.TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.data = {
            u'id': 3108351,
            u'timestamp_ms': u'1457792000000',
            u'text': 'my super tweet',
            u'retweet_count': 3,
            u'created_at': '2016-03-12T13:56:40Z',
            u'user': {
                u'id': 3108350,
                u'name': 'author',
                u'followers_count': 3,
            },
        }
        self.TwitterStream = TwitterStream()

    def test_tree(self):
        self.data['retweeted_status'] = {
            u'id': 3108350,
            u'timestamp_ms': u'1457791000000',
            u'text': 'original super tweet',
            u'created_at': '2016-03-12T13:56:40Z',
            u'retweet_count': 4,
            u'user': {
                u'id': 3108351,
                u'name': 'author',
                u'followers_count': 3,
            },
        }

        with freeze_time(datetime.fromtimestamp(1457792060, tz=pytz.utc)):
            tweet = self.TwitterStream.tweet_get_or_create(self.data)

        Fixture(
            'tweets/tests/test_tree.json',
            models=[Post, Stat],
        ).assertNoDiff()

    def test_sequence(self):
        fixture = [
            (4, 1457791000),
            (6, 1457792060),
            (9, 1457792120),
            (12, 1457792240),
            (30, 1457792300),
            (32, 1457792360),
        ]

        for count, ts in fixture:
            with freeze_time(datetime.fromtimestamp(ts, tz=pytz.utc)):
                self.data['retweet_count'] = count
                tweet = self.TwitterStream.tweet_get_or_create(self.data)

        Fixture(
            'tweets/tests/test_sequence.json',
            models=[Post, Stat],
        ).assertNoDiff()
