from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify

from datetime import datetime, timedelta
from dateutil import parser

import threading

from tweets.models import Retweets, Source, Tweet
from tweets.utils import get_auth, get_data, get_twitter

from twitter import TwitterStream

import pytz


class Command(BaseCommand):
    def handle(self, *args, **options):
        twitter_userstream = TwitterStream(
            auth=get_auth(),
            domain='userstream.twitter.com'
        )
        self.twitter = get_twitter()

        for msg in twitter_userstream.user():
            print 'Got msg', msg

            if 'friends' in msg:
                self.save_friends(msg['friends'])
                continue

            if 'id' not in msg:
                print 'Skipping because it has no id'
                continue


            tweet = Tweet.objects.create_from_data(msg)

            if 'retweeted_status' not in msg:
                def get_retweets():
                    data = get_data(tweet.id)

                    Retweets.objects.create(
                        tweet=tweet,
                        retweet_count=data['retweet_count'],
                        seconds_after_tweet=120,
                    )
                    print u'Saved retweets for %s after %s' % (
                        slugify(tweet),
                        120,
                    )
                threading.Timer(120, get_retweets).start()

            print u'Saved tweet %s' % slugify(tweet)

    def save_friends(self, ids):
        for l in [ids[i:i+100] for i in xrange(0, len(ids), 100)]:
            data = self.twitter.users.lookup(
                user_id=','.join([unicode(x) for x in l])
            )

            for user in data:
                Source.objects.create_from_data(user, friend=True)
                print u'Following %s' % slugify(user['name'])
