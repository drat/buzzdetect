import threading

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.template.defaultfilters import slugify

from posts.models import Post, Poster, Stat
from tweets.models import TwitterAccount

import pytz


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.monitor()

    @staticmethod
    def insert_retweets():
        now = datetime.now(tz=pytz.utc)

        tweets = Post.objects.posts_to_stat(1, 5)[:100]

        tweets_dict = {
            str(t.upstream_id): t for t in list(tweets)
        }

        ids = ','.join(tweets_dict.keys()[:100])

        if ids:
            account = TwitterAccount.objects.first()
            data = account.get_twitter().statuses.lookup(_id=ids)

            for tweet_data in data:
                tweet = tweets_dict[str(tweet_data['id'])]
                reposts = tweet_data['retweet_count']
                stat = Stat.objects.add_for_post(tweet, reposts, now)

                print u'Saved %s retweets for #%s aged %s in minute %s' % (
                    reposts,
                    tweet.upstream_id,
                    now - tweet.datetime,
                    stat.minute
                )

            print 'Done !'

            return account
        else:
            print 'Nothing to do !'

    @staticmethod
    def monitor():
        with transaction.atomic():
            account = Command.insert_retweets()

        # We can call this API 60 times per 15-minutes window that's every 15
        # seconds.
        threading.Timer(
            20,
            Command.monitor,
        ).start()
