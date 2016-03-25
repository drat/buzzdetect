from __future__ import unicode_literals

from datetime import datetime, timedelta

from dateutil import parser

from django.core.mail import send_mail
from django.db import models
from django import template
from django.utils.functional import cached_property

from manager_utils import manager_utils

import pytz


class SourceManager(models.Manager):
    def create_from_data(self, data, friend=None):
        try:
            source = self.get(id=data['id'])
        except self.model.DoesNotExist:
            source = self.create(
                id=data['id'],
                name=data['name'],
                friend=friend or False,
            )
        else:
            if friend and not source.friend:
                source.friend = True
                source.save()

        return source


class Source(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=150)
    friend = models.BooleanField(default=False)

    objects = SourceManager()


class TweetManager(models.Manager):
    def create_from_data(self, data):
        parent = None

        if 'retweeted_status' in data:
            retweeted = data['retweeted_status']

            try:
                parent = self.get(id=retweeted['id'])
            except self.model.DoesNotExist:
                parent = self.create(
                    id=retweeted['id'],
                    text=retweeted['text'],
                    datetime=parser.parse(retweeted['created_at']),
                    source=Source.objects.create_from_data(retweeted['user']),
                )

            retweet_count = retweeted['retweet_count']
        else:
            retweet_count = data['retweet_count']

        try:
            tweet = self.get(id=data['id'])
        except self.model.DoesNotExist:
            tweet = self.create(
                id=data['id'],
                parent=parent,
                text=data['text'],
                datetime=parser.parse(data['created_at']),
                source=Source.objects.create_from_data(data['user']),
            )

        target = parent if parent else tweet

        delta = datetime.now(pytz.utc) - target.datetime
        minutes = delta.seconds / 60.0

        retweet = Retweets.objects.create(
            tweet=target,
            retweet_count=retweet_count,
            retweet_per_minute=retweet_count / minutes,
            acceleration=0,
        )

        return tweet


class Tweet(models.Model):
    id = models.BigIntegerField(primary_key=True)
    parent = models.ForeignKey(
        'self',
        related_name='children',
        null=True,
        blank=True
    )

    text = models.CharField(max_length=180)
    datetime = models.DateTimeField()
    source = models.ForeignKey('Source')

    # Denormalized field handled by calculate_friends_retweets
    friends_retweets = models.PositiveIntegerField(default=0)

    objects = TweetManager()

    def calculate_friends_retweets(self):
        count = 0

        if self.source.friend:
            count += 1

        count += Tweet.objects.distinct().filter(
            parent=self,
            source__friend=True
        ).count()

        return count

    def __unicode__(self):
        return u'#%s %s' % (self.id, self.text)

    def get_twitter_url(self):
        return 'https://twitter.com/statuses/' + self.id


def calculate_friends_retweets(sender, instance, **kwargs):
    target = instance if not instance.parent_id else instance.parent
    previous = target.friends_retweets

    target.friends_retweets = target.calculate_friends_retweets()

    if previous != target.friends_retweets:
        target.save()

        if target.friends_retweets >= 2:
            send_mail(
                '[buzzdetect:%s] %s' % (
                    target.friends_retweets,
                    target.text,
                ),
                template.Template(
                    'tweets/buzz_mail.txt'
                ).render(template.Context({
                    'tweet': target,
                    'previous': previous,
                }))
            )
models.post_save.connect(calculate_friends_retweets, sender=Tweet)


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
