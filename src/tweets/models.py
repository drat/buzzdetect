from __future__ import unicode_literals

from datetime import datetime

from dateutil import parser

from django.db import models
from django.utils.functional import cached_property

from manager_utils import manager_utils

import pytz


class Tweet(models.Model):
    name = models.CharField(max_length=180)
    twitter_id = models.BigIntegerField()
    datetime = models.DateTimeField()

    def __unicode__(self):
        return u'#%s %s' % (self.twitter_id, self.name)

    def create_retweet_from_data(self, data):
        retweet = Retweets(
            tweet_id=self.pk,
            retweet_count=data['retweet_count'],
        )
        previous = retweet.previous

        if previous and retweet.retweet_count == previous.retweet_count:
            return

        retweet.save()

    @classmethod
    def create_from_data(cls, data):
        if 'retweeted_status' in data:
            data = data['retweeted_status']

        defaults = {
            'name': data['text'],
        }

        if 'timestamp_ms' in data:
            defaults['datetime'] = datetime.fromtimestamp(
                int(data['timestamp_ms']) / 1000.0,
                tz=pytz.utc
            )
        else:
            defaults['datetime'] = parser.parse(data['created_at'])

        tweet, created = manager_utils.upsert(
            Tweet.objects,
            twitter_id=int(data['id']),
            defaults=defaults
        )

        retweet_per_minute = 0
        delta = datetime.now(pytz.utc) - tweet.datetime
        minutes = delta.seconds / 60.0
        retweet_per_minute = data['retweet_count'] / minutes

        retweet = Retweets.objects.create(
            tweet=tweet,
            retweet_count=data['retweet_count'],
            retweet_per_minute=retweet_per_minute,
        )
        return tweet, created, retweet


class Retweets(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    tweet = models.ForeignKey('Tweet')
    retweet_count = models.PositiveIntegerField(default=0, db_index=True)
    retweet_per_minute = models.FloatField(default=0, db_index=True)
    acceleration = models.FloatField(default=0, db_index=True)

    @cached_property
    def previous(self):
        return Retweets.objects.filter(
            tweet=self.tweet,
        ).order_by(
            '-datetime'
        ).first()

    def calculate(self):
        if not self.previous:
            return 0, 0

        compare_datetime = self.datetime or datetime.now(pytz.utc)
        new_retweets = self.retweet_count - self.previous.retweet_count
        delta = compare_datetime - self.previous.datetime
        minutes = delta.seconds / 60.0

        retweet_per_minute = (
            0 if not new_retweets else new_retweets / minutes
        )

        acceleration = (
            self.retweet_per_minute - self.previous.retweet_per_minute
        )

        return retweet_per_minute, acceleration

    class Meta:
        ordering = ('acceleration',)
        unique_together = (
            ('datetime', 'tweet')
        )


def process_retweets(sender, instance, **kwargs):
    if instance.retweet_per_minute and instance.acceleration:
        return

    instance.retweet_per_minute, instance.acceleration = instance.calculate()
models.signals.pre_save.connect(process_retweets, sender=Retweets)
