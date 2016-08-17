from django import test

from .tests import PostsTestMixin


class StatTest(PostsTestMixin, test.TransactionTestCase):
    def assertLastStatIs(self, post, minute, reposts, speed, acceleration):
        self.assertEqual(post.last_stat.minute, minute)
        self.assertEqual(post.last_stat.reposts, reposts)
        self.assertAlmostEqual(post.last_stat.speed, speed, 3)
        self.assertAlmostEqual(post.last_stat.acceleration, acceleration, 3)

    def test_stat_add_for_post(self):
        poster0 = self.create_poster()
        post0 = self.create_post(10)
        self.assertEqual(post0.last_stat, None)

        stat0 = self.add_stat(post0, 1, 1)
        self.assertEqual(post0.last_stat, stat0)
        self.assertLastStatIs(post0, 1, 1, 1, 1)

        stat1 = self.add_stat(post0, 2, 2)
        self.assertEqual(post0.last_stat, stat1)
        self.assertLastStatIs(post0, 2, 2, 1, 0)

        stat2 = self.add_stat(post0, 3, 4)
        self.assertLastStatIs(post0, 3, 4, 2, 1)
        self.assertEqual(post0.last_stat, stat2)

        stat2 = self.add_stat(post0, 4, 5)
        self.assertLastStatIs(post0, 4, 5, 1, -1)
        self.assertEqual(post0.last_stat, stat2)

    def test_average_compare(self):
        post0 = self.create_post()
        self.add_stat(post0, 1, 2)

        post1 = self.create_post()
        self.add_stat(post1, 1, 2)

        self.assertEqual(self.friend.average_set.get(minute=1).average, 2)

        self.add_stat(post0, 2, 4)
        self.assertEqual(self.friend.average_set.get(minute=1).average, 2)
        self.assertEqual(self.friend.average_set.get(minute=2).average, 4)

        self.add_stat(post1, 2, 7)
        self.assertEqual(self.friend.average_set.get(minute=1).average, 2)
        self.assertEqual(self.friend.average_set.get(minute=2).average, 5.5)

    def test_friends_reposts(self):
        post0 = self.create_post()
        stat0 = self.add_stat(post0, 1, 4)
        self.assertEqual(stat0.friends_reposts, 1)

        post1 = self.create_post(
            parent=post0,
            poster=self.create_poster(friend=True)
        )
        stat1 = self.add_stat(post0, 2, 6)
        self.assertEqual(stat1.friends_reposts, 2)

        post2 = self.create_post(parent=post0, poster=self.create_poster())
        stat2 = self.add_stat(post0, 3, 8)
        self.assertEqual(stat2.friends_reposts, 2)

        stat_post2 = self.add_stat(post2, 2, 6)
        self.assertEqual(stat_post2.friends_reposts, 0)

    def test_reposts_per_followers_count(self):
        post0 = self.create_post(poster=self.create_poster(followers_count=10))
        stat1 = self.add_stat(post0, 1, 8)
        self.assertEquals(stat1.reposts_per_followers_count, 0.8)
        stat2 = self.add_stat(post0, 2, 10)
        self.assertEquals(stat2.reposts_per_followers_count, 1)
        stat3 = self.add_stat(post0, 3, 15)
        self.assertEquals(stat3.reposts_per_followers_count, 1.5)
