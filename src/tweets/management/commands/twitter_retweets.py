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
            Tweet.objects.order_by('-last_retweets__acceleration')[:7]
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
