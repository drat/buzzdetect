from datetime import datetime

from dbdiff.fixture import Fixture

from django import test

from freezegun import freeze_time

import pytz

from tweets.models import Retweets, Tweet


class CreateTweetFromMsg(test.TransactionTestCase):
    reset_sequences = True

    def test_create_from_msg(self):
        data = {
            u'id': 3108351,
            u'timestamp_ms': u'1457792000000',
            u'text': 'my super tweet',
            u'retweet_count': 3,
        }
        with freeze_time(datetime.fromtimestamp(1457792060, tz=pytz.utc)):
            tweet, created, retweet = Tweet.create_from_msg(data)

        with freeze_time(datetime.fromtimestamp(1457792120, tz=pytz.utc)):
            data['retweet_count'] = 6
            tweet.create_retweet(data)

        with freeze_time(datetime.fromtimestamp(1457792180, tz=pytz.utc)):
            data['retweet_count'] = 9
            tweet.create_retweet(data)

        with freeze_time(datetime.fromtimestamp(1457792240, tz=pytz.utc)):
            data['retweet_count'] = 12
            tweet.create_retweet(data)

        with freeze_time(datetime.fromtimestamp(1457792300, tz=pytz.utc)):
            data['retweet_count'] = 30
            tweet.create_retweet(data)

        with freeze_time(datetime.fromtimestamp(1457792360, tz=pytz.utc)):
            data['retweet_count'] = 32
            tweet.create_retweet(data)

        Fixture(
            'tweets/tests/test_sequence.json',
            models=[Tweet, Retweets],
        ).assertNoDiff()
