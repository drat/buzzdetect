import threading

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify

from posts.models import Post, Poster, Stat
from tweets.utils import get_twitter

import pytz


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.monitor()

    @staticmethod
    def monitor():
        twitter = get_twitter()

        now = datetime.now(tz=pytz.utc)

        all_tweets = Post.objects.filter(
            parent=None,
        ).order_by(
            '-datetime',
        )

        recent = all_tweets.filter(
            datetime__gte=now - timedelta(minutes=5),
        )

        def get_older_tweets(min_minutes, max_minutes, stats_minutes):
            return all_tweets.filter(
                added__lt=now - timedelta(minutes=min_minutes),
                added__gte=now - timedelta(minutes=max_minutes),
            ).exclude(
                id__in=Stat.objects.filter(
                    added__gte=now - timedelta(minutes=stats_minutes),
                ).order_by('-added').values_list('post_id')
            )

        tweets = list(recent)
        series = (
            (5, 30, 1),
            (30, 100, 5),
            (100, 200, 10),
            (200, 300, 20),
            (300, 1000, 60),
            (1000, 10000, 120),
        )

        for args in series:
            if len(tweets) >= 100:
                print 'Stopped at', args
                break
            tweets += get_older_tweets(*args)

        tweets_dict = {
            str(t.upstream_id): t for t in list(tweets)
        }

        ids = ','.join(tweets_dict.keys()[:100])

        if ids:
            data = twitter.statuses.lookup(_id=ids)

            for tweet_data in data:
                tweet = tweets_dict[str(tweet_data['id'])]
                reposts = tweet_data['retweet_count']
                stat = tweet.stat_set.create(reposts=reposts)
                tweet.last_stat = stat

                print u'Saved %s retweets for #%s aged %s' % (
                    reposts,
                    tweet.upstream_id,
                    now - tweet.added,
                )

            print 'Done !'

        # We can call this API 60 times per 15-minutes window that's every 15
        # seconds. Let's use every 20 seconds for now.
        threading.Timer(
            20,
            Command.monitor,
        ).start()
