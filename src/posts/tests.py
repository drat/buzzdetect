from datetime import datetime, timedelta

import pytz

from django.contrib.contenttypes.models import ContentType

from tweets.models import TwitterAccount

from .models import Post, Poster, PosterAverageStat, Stat


class PostsTestMixin(object):
    # Make this a class attribute
    upstream_id = 1

    def setUp(self):
        self.upstream_id = 1
        self.account = TwitterAccount.objects.create(
            consumer_key='aoeu',
            consumer_secret='aoeu',
            token='aoeu',
            secret='aoeu',
        )
        self.friend = self.create_poster(friend=True)

    def create_post(self, minute=None, second=None, poster=None,
            parent=None):

        self.upstream_id += 1

        return Post.objects.create(
            upstream_id=self.upstream_id,
            poster=poster or self.friend,
            content='',
            parent=parent,
            datetime=self.get_datetime(minute or 30, second or 0),
            content_type=ContentType.objects.get_for_model(self.account),
            object_id=self.account.pk,
        )

    def create_poster(self, friend=False, followers_count=None):
        self.upstream_id += 1
        return Poster.objects.create(
            upstream_id=self.upstream_id,
            name='friend',
            followers_count=followers_count or 10,
            friend=friend,
            content_type=ContentType.objects.get_for_model(self.account),
            object_id=self.account.pk,
        )

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
