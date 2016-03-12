from django.core.management.base import BaseCommand

from tweets.models import Tweet
from tweets.utils import get_auth

from twitter import TwitterStream


class Command(BaseCommand):
    def handle(self, *args, **options):
        twitter_userstream = TwitterStream(
            auth=get_auth(),
            domain='userstream.twitter.com'
        )

        for msg in twitter_userstream.user():
            if 'id' not in msg:
                continue

            tweet, created, retweet = Tweet.create_from_msg(msg)
