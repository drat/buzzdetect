from __future__ import unicode_literals

from datetime import datetime

from django.db import models

from manager_utils import manager_utils

import pytz


class Tweet(models.Model):
    name = models.CharField(max_length=180)
    twitter_id = models.BigIntegerField()
    datetime = models.DateTimeField()

    def __unicode__(self):
        return self.name

    def create_retweet(self, data):
        retweet_count = data['retweet_count']

        Retweets.objects.create(
            tweet_id=self.pk,
            retweet_count=retweet_count,
        )

    @classmethod
    def create_from_msg(cls, msg):
        tweet, created = manager_utils.upsert(
            Tweet.objects,
            twitter_id=int(msg['id']),
            defaults={
                'name': msg['text'],
                'datetime': datetime.fromtimestamp(
                    int(msg['timestamp_ms']) / 1000.0,
                    tz=pytz.utc
                ),
            }
        )

        delta = datetime.now(pytz.utc) - tweet.datetime
        minutes = delta.seconds / 60.0

        retweet = Retweets.objects.create(
            tweet=tweet,
            retweet_count=msg['retweet_count'],
            retweet_per_minute=msg['retweet_count'] / minutes,
            acceleration=0,
        )
        return tweet, created, retweet


class Retweets(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    tweet = models.ForeignKey('Tweet')
    retweet_count = models.PositiveIntegerField(default=0, db_index=True)
    retweet_per_minute = models.FloatField(default=0, db_index=True)
    acceleration = models.FloatField(default=0, db_index=True)

    class Meta:
        ordering = ('acceleration',)
        unique_together = (
            ('datetime', 'tweet')
        )


def process_retweets(sender, instance, **kwargs):
    last = Retweets.objects.filter(
        tweet=instance.tweet
    ).order_by(
        '-datetime'
    ).first()

    if last is None:
        return

    retweets = instance.retweet_count - last.retweet_count
    delta = datetime.now(pytz.utc) - last.datetime
    minutes = delta.seconds / 60.0

    instance.retweet_per_minute = 0 if not retweets else retweets / minutes

    instance.acceleration = (
        instance.retweet_per_minute - last.retweet_per_minute
    )
models.signals.pre_save.connect(process_retweets, sender=Retweets)
