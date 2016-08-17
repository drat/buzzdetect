from django import test
from django.db import transaction

from .tests import PostsTestMixin


class PostsToStatTest(PostsTestMixin, test.TransactionTestCase):
    def test_friend_reposts_of_external(self):
        post = self.create_post(poster=self.create_poster())

        transaction.commit()
        post.refresh_from_db()
        self.add_stat(post, 1, 1)
        self.assertEqual(post.last_stat.friends_reposts, 0)

        self.create_post(parent=post)
        transaction.commit()
        self.add_stat(post, 2, 2)
        post.refresh_from_db()

        self.assertEqual(post.last_stat.friends_reposts, 1)

    def test_friend_reposts_of_friend(self):
        post = self.create_post(poster=self.create_poster(friend=True))

        transaction.commit()
        post.refresh_from_db()
        self.add_stat(post, 1, 1)
        self.assertEqual(post.last_stat.friends_reposts, 1)

        self.create_post(parent=post)
        transaction.commit()
        self.add_stat(post, 2, 2)
        post.refresh_from_db()

        self.assertEqual(post.last_stat.friends_reposts, 2)
