from datetime import datetime

from django import test
from django.db import transaction

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


