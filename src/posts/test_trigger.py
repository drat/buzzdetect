from datetime import datetime

from django import test
from django.db import transaction

from posts.models import Post, Poster, Stat


class TestTrigger(test.TransactionTestCase):
    def test_friends_repost(self):
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

        stat2 = Stat.objects.get(pk=stat2.pk)
        self.assertEqual(stat2.friends_reposts, 2)
