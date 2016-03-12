from django.core.management.base import BaseCommand

from tweets.models import Tweet
from tweets.utils import get_auth

from twitter import Twitter


class Command(BaseCommand):
    def handle(self, *args, **options):
        twitter = Twitter(auth=get_auth())

        for tweet in Tweet.objects.all():
            data = twitter.statuses.show(_id=tweet.twitter_id)
            tweet.create_retweet(data)
