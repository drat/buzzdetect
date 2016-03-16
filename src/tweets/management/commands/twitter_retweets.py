from django.core.management.base import BaseCommand

from tweets.models import Tweet
from tweets.utils import get_data


class Command(BaseCommand):
    def handle(self, *args, **options):
        tweets = list(Tweet.objects.filter(last=None)[:20])

        if 20 - len(tweets) > 0:
            tweets = Tweet.objects.order_by('-total_rtm')[:20-len(tweets)]

        for tweet in tweets:
            data = get_data(tweet.twitter_id)

            if not data:
                continue

            tweet.create_retweet_from_data(data)

            print 'Saved retweet for', tweet
