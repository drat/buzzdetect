from django.core.management.base import BaseCommand

from tweets.models import Tweet
from tweets.utils import get_data


class Command(BaseCommand):
    def handle(self, *args, **options):
        for tweet in Tweet.objects.all():
            data = get_data(tweet.twitter_id)

            if not data:
                continue

            tweet.create_retweet_from_data(data)

            print 'Saved retweet for', tweet
