from datetime import datetime, timedelta
import random

from django import test
from django.db import connection, transaction
from django.utils import timezone

from posts.models import Post, Poster, Stat


class TriggerTest(test.TransactionTestCase):
    def setUp(self):
        self.friend = Poster(
            upstream_id=1,
            name='friend',
            followers_count=0,
            friend=True,
        )
        self.friend.save()

        self.post = Post.objects.create(
            upstream_id=1,
            poster=self.friend,
            content='',
            datetime=datetime.now(),
        )

        stat = Stat.objects.create(
            post=self.post,
            reposts=2,
        )

        self.post2 = Post.objects.create(
            parent=self.post,
            upstream_id=2,
            poster=self.friend,
            content='',
            datetime=datetime.now(),
        )

        stat2 = Stat.objects.create(
            post=self.post,
            reposts=3,
        )
        transaction.commit()
        self.stat2 = Stat.objects.get(pk=stat2.pk)


class FriendsRepostsTest(TriggerTest):
    def test_friends_repost(self):
        self.assertEqual(self.stat2.friends_reposts, 2)


class PosterAvegareStatTest(test.TransactionTestCase):
    def setUp(self):
        self.counter = random.randint(123321, 21312343)

        self.poster0 = Poster.objects.create(
            upstream_id=self.get_int(),
            name='poster0',
            followers_count=0,
            friend=True,
        )

        self.poster1 = Poster.objects.create(
            upstream_id=self.get_int(),
            name='poster1',
            followers_count=0,
            friend=True,
        )

    def get_int(self):
        self.counter += 1
        return self.counter

    def get_average_stat(self, poster, seconds):
        seconds = seconds or 120
        return poster.average_set.filter(
            seconds=seconds
        ).first()

    def add_stat(self, post, seconds, reposts):
        if isinstance(post, Poster):
            post = self.add_post(post)

        return post.stat_set.create(
            reposts=reposts,
            added=post.datetime + timedelta(seconds=seconds)
        )

    def assert_average_stat_is(self, poster, seconds, posts, reposts, average):
        stat = self.get_average_stat(poster, seconds)
        self.assertEqual(stat.total_posts, posts)
        self.assertEqual(stat.total_reposts, reposts)
        self.assertEqual(stat.seconds, seconds)
        self.assertEqual(stat.average, average)

    def add_post(self, poster):
        return poster.post_set.create(
            upstream_id=self.get_int(),
            content=self.id(),
            datetime=timezone.now(),
        )

    def test_average_stat_after_120_seconds(self):
        self.add_stat(self.poster0, 120, 10)
        self.assert_average_stat_is(self.poster0, 120, 1, 10, 10)

        stat = self.add_stat(self.poster0, 100, 3)  # noise, should be ignored
        stat = self.add_stat(self.poster0, 129, 6)
        stat = self.add_stat(self.poster0, 140, 15)  # noise
        self.assert_average_stat_is(self.poster0, 120, 2, 16, 8)

        # test that noise doesn't affect result for poster0
        self.add_stat(self.poster1, 120, 4)
        self.assert_average_stat_is(self.poster0, 120, 2, 16, 8)

        self.add_stat(self.poster0, 120, 17)
        self.add_stat(self.poster0, 145, 15)  # noise
        self.assert_average_stat_is(self.poster0, 120, 3, 33, 11)

        self.assertEquals(
            Poster.objects.get(pk=self.poster0.pk).average_after_two_minute,
            self.get_average_stat(self.poster0, 120)
        )
