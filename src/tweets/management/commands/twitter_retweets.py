from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from tweets.models import Tweet, Retweets
from tweets.utils import get_data

import pytz


class Command(BaseCommand):
    def handle(self, *args, **options):
        min_datetime = (
            datetime.now(tz=pytz.utc)
            - timedelta(minutes=100)
        )

        recent_leafs = Tweet.objects.filter(
            parent=None,
            datetime__gte=min_datetime,
        )

        # First we want tweets with most retweets
        tweets = list(
            recent_leafs.filter(
                friends_retweets__gte=2
            ).order_by(
                '-friends_retweets'
            )[:10]
        )

        # Let's check random buzz while we're at it
        tweets += list(
            recent_leafs.order_by('-total_rtm')[:7]
        )

        tweets += list(
            recent_leafs.order_by('-last_retweets__acceleration')[:7]
        )

        for tweet in set(tweets):
            print "Flashing tweet", tweet

            data = get_data(tweet.id)

            if data == 'deleted':
                tweet.delete()
                continue

            if not data:
                continue

            retweets = Retweets.objects.create(
                tweet=tweet,
                retweet_count=data['retweet_count'],
            )
