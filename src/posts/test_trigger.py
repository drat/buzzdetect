from datetime import datetime, timedelta
import random

from django import test
from django.contrib.contenttypes.models import ContentType
from django.db import connection, transaction
from django.utils import timezone

from posts.models import Post, Poster, Stat
from tweets.models import TwitterAccount


class TriggerTest(test.TransactionTestCase):
    def setUp(self):
        self.account = TwitterAccount.objects.create(
            consumer_key='aoeu',
            consumer_secret='aoeu',
            token='aoeu',
            secret='aoeu',
        )

        self.friend = Poster.objects.create(
            upstream_id=1,
            name='friend',
            followers_count=0,
            friend=True,
            content_type=ContentType.objects.get_for_model(self.account),
            object_id=self.account.pk,
        )

        self.post = Post.objects.create(
            upstream_id=1,
            poster=self.friend,
            content='',
            datetime=datetime.now(),
            content_type=ContentType.objects.get_for_model(self.account),
            object_id=self.account.pk,
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
            content_type=ContentType.objects.get_for_model(self.account),
            object_id=self.account.pk,
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

        self.account = TwitterAccount.objects.create(
            consumer_key='aoeu',
            consumer_secret='aoeu',
            token='aoeu',
            secret='aoeu',
        )

        self.poster0 = Poster.objects.create(
            upstream_id=self.get_int(),
            name='poster0',
            followers_count=0,
            friend=True,
            content_type=ContentType.objects.get_for_model(self.account),
            object_id=self.account.pk,
        )

        self.poster1 = Poster.objects.create(
            upstream_id=self.get_int(),
            name='poster1',
            followers_count=0,
            friend=True,
            content_type=ContentType.objects.get_for_model(self.account),
            object_id=self.account.pk,
        )

    def get_int(self):
        self.counter += 1
        return self.counter

    def get_average_stat(self, poster, seconds):
        return poster.average_set.filter(
            seconds=seconds
        ).first()

    def add_stat(self, post, seconds, reposts):
        if isinstance(post, Poster):
            post = self.add_post(post)

        stat = post.stat_set.create(
            reposts=reposts,
            added=post.datetime + timedelta(seconds=seconds)
        )
        stat.post.refresh_from_db()
        return stat

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
            content_type=ContentType.objects.get_for_model(self.account),
            object_id=self.account.pk,
        )

    def test_zero_reposts_at_two_minute(self):
        ''' Regression test against a division by zero '''
        poster = Poster.objects.create(
            upstream_id=self.get_int(),
            name='poster0',
            followers_count=0,
            friend=True,
            content_type=ContentType.objects.get_for_model(self.account),
            object_id=self.account.pk,
        )

        stat0 = self.add_stat(poster, 120, 0)
        stat1 = self.add_stat(poster, 120, 0)
        self.assert_average_stat_is(poster, 120, 2, 0, 0)

        stat2 = self.add_stat(poster, 180, 0)
        stat3 = self.add_stat(poster, 180, 0)
        self.assert_average_stat_is(poster, 180, 2, 0, 0)
        self.assertEqual(stat2.post.average_compare_after_three_minute, 0)
        self.assertEqual(stat3.post.average_compare_after_three_minute, 0)

    def test_average_stat(self):
        # trigger debug incantation
        # before = len(connection.connection.notices)
        # for notice in connection.connection.notices[before:]:
        #     print notice

        stat0 = self.add_stat(self.poster0, 120, 10)
        self.assert_average_stat_is(self.poster0, 120, 1, 10, 10)
        self.assertEqual(stat0.post.average_compare_after_three_minute, None)

        stat1 = self.add_stat(self.poster0, 180, 10)
        # Should not have been modified
        self.assert_average_stat_is(self.poster0, 120, 1, 10, 10)

        # Should have been added
        self.assert_average_stat_is(self.poster0, 180, 1, 10, 10)
        self.assertEqual(stat1.post.average_compare_after_three_minute, 1)

        self.add_stat(self.poster0, 100, 3)  # noise, should be ignored
        stat2 = self.add_stat(self.poster0, 129, 6)
        self.add_stat(self.poster0, 140, 15)  # noise
        # Should have updated
        self.assert_average_stat_is(self.poster0, 120, 2, 16, 8)
        # Should have not been updated
        self.assert_average_stat_is(self.poster0, 180, 1, 10, 10)
        self.assertEqual(stat0.post.average_compare_after_three_minute, None)
        self.assertEqual(stat1.post.average_compare_after_three_minute, 1)
        self.assertEqual(stat2.post.average_compare_after_three_minute, None)

        # test that noise doesn't affect result for poster0
        stat3 = self.add_stat(self.poster1, 120, 4)
        # Should not have been updated after adding a stat for poster1
        self.assert_average_stat_is(self.poster0, 120, 2, 16, 8)
        self.assert_average_stat_is(self.poster0, 180, 1, 10, 10)
        self.assertEqual(stat3.post.average_compare_after_three_minute, None)

        stat4 = self.add_stat(self.poster0, 120, 17)
        self.add_stat(self.poster0, 145, 15)  # noise
        # Should have been updated
        self.assert_average_stat_is(self.poster0, 120, 3, 33, 11)
        # Should have not been updated
        self.assert_average_stat_is(self.poster0, 180, 1, 10, 10)

        stat5 = self.add_stat(self.poster0, 180, 2)
        self.add_stat(self.poster0, 199, 15)  # noise
        # Should have been updated
        self.assert_average_stat_is(self.poster0, 180, 2, 12, 6)
        self.assertEqual(int(stat5.post.average_compare_after_three_minute * 100), 33)

        # Test denormalized average_after column
        self.assertEquals(
            Poster.objects.get(pk=self.poster0.pk).average_after_two_minute,
            self.get_average_stat(self.poster0, 120)
        )

        self.assertEquals(
            Poster.objects.get(pk=self.poster0.pk).average_after_three_minute,
            self.get_average_stat(self.poster0, 180)
        )
