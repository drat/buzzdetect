from datetime import datetime

from dbdiff.fixture import Fixture

from django import test

from freezegun import freeze_time

import pytz

from tweets.models import Retweets, Tweet


class CreateTweetFromMsg(test.TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.data = {
            u'id': 3108351,
            u'timestamp_ms': u'1457792000000',
            u'text': 'my super tweet',
            u'retweet_count': 3,
        }

    def test_tree(self):
        self.data['retweeted_status'] = {
            u'id': 3108350,
            u'timestamp_ms': u'1457791000000',
            u'text': 'original super tweet',
            u'retweet_count': 4,
        }

        with freeze_time(datetime.fromtimestamp(1457792060, tz=pytz.utc)):
            tweet, created, retweet = Tweet.create_from_data(self.data)

        Fixture(
            'tweets/tests/test_tree.json',
            models=[Tweet, Retweets],
        ).assertNoDiff()

    def test_sequence(self):
        with freeze_time(datetime.fromtimestamp(1457792060, tz=pytz.utc)):
            tweet, created, retweet = Tweet.create_from_data(self.data)

        with freeze_time(datetime.fromtimestamp(1457792120, tz=pytz.utc)):
            self.data['retweet_count'] = 6
            tweet.create_retweet_from_data(self.data)

        with freeze_time(datetime.fromtimestamp(1457792180, tz=pytz.utc)):
            self.data['retweet_count'] = 9
            tweet.create_retweet_from_data(self.data)

        with freeze_time(datetime.fromtimestamp(1457792240, tz=pytz.utc)):
            self.data['retweet_count'] = 12
            tweet.create_retweet_from_data(self.data)

        with freeze_time(datetime.fromtimestamp(1457792300, tz=pytz.utc)):
            self.data['retweet_count'] = 30
            tweet.create_retweet_from_data(self.data)

        with freeze_time(datetime.fromtimestamp(1457792360, tz=pytz.utc)):
            self.data['retweet_count'] = 32
            tweet.create_retweet_from_data(self.data)

        Fixture(
            'tweets/tests/test_sequence.json',
            models=[Tweet, Retweets],
        ).assertNoDiff()
