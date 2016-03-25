from django.core.management.base import BaseCommand

from tweets.models import Tweet, Retweets
from tweets.utils import get_data


class Command(BaseCommand):
    def handle(self, *args, **options):
        tweets = list(
            Tweet.objects.exclude(
                total_rtm=None,
            ).order_by('-total_rtm')[:3]
        )

        tweets += list(
            Tweet.objects.order_by('-last__acceleration')[:7]
        )

        tweets += list(
            Tweet.objects.filter(
                skips__lte=3,
            ).order_by('skips', '-total_rtm')[:5]
        )

        for tweet in set(tweets):
            print "Flashing tweet", tweet

            data = get_data(tweet.twitter_id)

            if data == 'deleted':
                tweet.delete()
                continue

            if not data:
                continue

            tweet.create_retweet_from_data(data)
