from datetime import datetime, timedelta

import pytz

from django.contrib.contenttypes.models import ContentType

from tweets.models import TwitterAccount

from .models import Hub, Post, Poster, PosterAverageStat, Stat


class PostsTestMixin(object):
    # Make this a class attribute
    upstream_id = 1

    def setUp(self):
        self.upstream_id = 1
        self.hub0, c = Hub.objects.get_or_create(name='hub0')
        self.hub1, c = Hub.objects.get_or_create(name='hub1')
        self.account0, c = TwitterAccount.objects.get_or_create(
            consumer_key='aoeu',
            consumer_secret='aoeu',
            token='aoeu',
            secret='aoeu',
            hub=self.hub0,
        )
        self.account1, c = TwitterAccount.objects.get_or_create(
            consumer_key='aoeu',
            consumer_secret='aoeu',
            token='aoeu',
            secret='aoeu',
            hub=self.hub1,
        )
        self.friend = self.create_poster(friend=True)

    def create_post(self, minute=None, second=None, poster=None,
            parent=None, account=None):

        self.upstream_id += 1

        return Post.objects.create(
            upstream_id=self.upstream_id,
            poster=poster or self.friend,
            content='',
            parent=parent,
            datetime=self.get_datetime(minute or 30, second or 0),
            account=account or self.account0.account_ptr
        )

    def create_poster(self, friend=False, followers_count=None):
        self.upstream_id += 1
        poster = Poster.objects.create(
            upstream_id=self.upstream_id,
            name='friend',
            followers_count=followers_count or 10,
            friend=friend,
        )
        poster.accounts.add(self.account0.account_ptr)
        return poster

    def add_stat(self, post, minute, reposts):
        stat = Stat.objects.add_for_post(
            post,
            reposts,
            post.datetime + timedelta(minutes=minute)
        )
        # update last_stat
        post.refresh_from_db()
        return stat

    def get_datetime(self, minute=None, seconds=None):
        return datetime(2000, 1, 1, 12,
                minute or 30, seconds or 0, tzinfo=pytz.utc)
