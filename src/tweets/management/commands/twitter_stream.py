from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify
from django.conf import settings

from dateutil import parser

import threading

from posts.models import Post, Poster

import time

from tweets.utils import get_auth, get_data, get_twitter

from twitter import TwitterStream
from twitter.api import TwitterHTTPError


class Command(BaseCommand):
    def handle(self, *args, **options):
        while True:
            try:
                self.follow_stream()
            except TwitterHTTPError as e:
                print e
                time.sleep(10)

    def follow_stream(self):
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

            if 'delete' in msg and 'status' in msg['delete']:
                Post.objects.filter(
                    upstream_id=msg['delete']['status']['id']
                ).delete()
                print 'Deleted', msg
                continue

            if 'id' not in msg:
                print 'Skipping because it has no id'
                continue

            tweet = self.tweet_get_or_create(msg)
            print u'Saved tweet %s' % slugify(tweet)

    def save_friends(self, ids):
        for l in [ids[i:i+100] for i in xrange(0, len(ids), 100)]:
            data = self.twitter.users.lookup(
                user_id=','.join([unicode(x) for x in l])
            )

            for user in data:
                tweeter = self.tweetter_get_or_create(user, friend=True)
                print u'Following %s' % slugify(user['name'])

    def tweet_get_or_create(self, data):
        parent = None

        if 'retweeted_status' in data:
            parent = self.tweet_get_or_create(data['retweeted_status'])

        poster = self.tweetter_get_or_create(data['user'])

        defaults = dict(
            parent=parent,
            poster=poster,
            datetime=parser.parse(data['created_at']),
            content=data['text'],
        )

        obj, created = Post.objects.update_or_create(
            upstream_id=data['id'],
            defaults=defaults,
        )

        return obj

    def tweetter_get_or_create(self, data, friend=None):
        defaults = dict(
            name=data['name'],
            followers_count=data['followers_count'],
        )

        if friend is not None:
            defaults['friend'] = friend

        obj, created = Poster.objects.update_or_create(
            upstream_id=data['id'],
            defaults=defaults,
        )

        return obj
