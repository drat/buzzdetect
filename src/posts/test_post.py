from django import test
from django.apps import apps
from django.contrib.auth import get_user_model

from .forms import PostSearchForm

from .models import Post, Poster

from .tests import PostsTestMixin


class PostsToStatTest(PostsTestMixin, test.TransactionTestCase):
    def test_posts_to_stat(self):
        include = [
            (27, 50),
            (28, 0),
            (28, 10),
            (28, 50),
            (29, 0),
            (29, 10),
        ]

        exclude = [
            (28, 11),
            (28, 11),
            (28, 49),
            (29, 11),
            (29, 49),
            # too old
            (21, 0),
            (21, 10),
        ]

        expected = [self.create_post(*args).pk for args in include]
        unexpected = [self.create_post(*args).pk for args in exclude]

        self.assertEqual(
            list(
                Post.objects.posts_to_stat(
                    1,
                    5,
                    self.get_datetime(30),
                ).order_by('pk').values_list(
                    'pk',
                    flat=True
                )
            ),
            expected
        )

    def test_post_minute(self):
        tests = [
            (26, 10, 4),
            (26, 30, 4),
            (26, 31, 3),
            (27, 10, 3),
            (27, 30, 3),
            (27, 31, 2),
            (27, 50, 2),
            (28, 10, 2),
            (28, 31, 1),
        ]

        for test in tests:
            post = self.create_post(*test[:2])
            result = post.minutes_since(
                self.get_datetime(30),
            )
            self.assertEqual(
                test[2],
                result,
                'Expected post at %s:%s to be at minute %s' % test +
                ' ot instead %s' % result
            )


class PostFilterTest(PostsTestMixin, test.TransactionTestCase):
    def setUp(self):
        self.superuser, c = get_user_model().objects.get_or_create(
            username='superuser',
            is_superuser=True,
        )
        Poster.objects.all().delete()

        super(PostFilterTest, self).setUp()

        self.friend_post0 = self.create_post()
        self.add_stat(self.friend_post0, 1, 4)

        self.friend_repost0 = self.create_post(
            parent=self.friend_post0,
            poster=self.create_poster(friend=True),
        )
        # Now we can add stat for minute 2 of friend_post0 so that it sets the
        # friends_repost count in stat for minute 2
        self.add_stat(self.friend_post0, 2, 5)
        self.add_stat(self.friend_post0, 3, 60)

        self.other_repost0 = self.create_post(
            parent=self.friend_post0,
            poster=self.create_poster(followers_count=100),
            minute=32,
            account=self.account1,
            kind=2,
        )

        self.add_stat(self.other_repost0, 1, 2)
        self.add_stat(self.other_repost0, 2, 10)
        self.add_stat(self.other_repost0, 3, 38)

        self.friend_post1 = self.create_post(kind=2)
        self.add_stat(self.friend_post1, 1, 6)
        self.add_stat(self.friend_post1, 2, 18)
        self.add_stat(self.friend_post1, 3, 20)

        self.other_post1 = self.create_post(
            poster=self.other_repost0.poster,
            account=self.account1,
            kind=3,
        )
        self.add_stat(self.other_post1, 1, 1)
        self.add_stat(self.other_post1, 2, 25)
        self.add_stat(self.other_post1, 3, 28)

        # hack because average compare is calculated at the moment the stat is
        # inserted
        #for stat in Stat.objects.all():
        #    stat.average_compare =

    def assertResultEquals(self, *expected, **kwargs):
        result = list(Post.objects.filter_list(**kwargs))
        self.assertEqual([r['id'] for r in result], list(expected))

        # Try with the form now
        form, result = PostSearchForm.post_list(user=self.superuser, data=kwargs)
        self.assertEqual([r['id'] for r in result], list(expected))

    def test_filter(self):
        # test_min_average_compare_on_last
        self.assertResultEquals(
            self.other_repost0.pk,
            self.friend_post0.pk,
            min_average_compare=1,
        )

        # test_min_average_compare_on_minute_on
        self.assertResultEquals(
            self.other_repost0.pk,
            self.friend_post1.pk,
            min_average_compare=1,
            filter_on_stat=1,
        )


        # test_min_average_compare_on_two_minute
        self.assertResultEquals(
            self.other_post1.pk,
            self.friend_post1.pk,
            min_average_compare=1,
            filter_on_stat=2,
        )

        # test at three minute
        self.assertResultEquals(
            self.other_repost0.pk,
            self.friend_post0.pk,
            min_average_compare=1,
            filter_on_stat=3,
        )

        # test_max_age_in_minutes
        self.assertResultEquals(
            self.other_repost0.pk,
            min_average_compare=1,
            filter_on_stat=3,
            max_age_in_minutes=1,
            now=self.get_datetime(minute=33),
        )

        # test_min_friend_reposts_on_last
        self.assertResultEquals(
            self.friend_post0.pk,
            min_friends_reposts=2,
        )

        # test_min_friend_reposts_on_one_minute
        self.assertResultEquals(
            min_friends_reposts=2,
            filter_on_stat=1,
        )

        # test_min_friend_reposts_on_two_minute
        self.assertResultEquals(
            self.friend_post0.pk,
            min_friends_reposts=2,
            filter_on_stat=2,
        )

        # test_order_by_friends_reposts
        self.assertResultEquals(
            self.friend_post0.pk,
            self.friend_post1.pk,
            self.other_post1.pk,
            self.other_repost0.pk,
            order_by='s.friends_reposts DESC',
        )

        # order by friend repost on minute 1
        self.assertResultEquals(
            self.friend_post1.pk,
            self.friend_post0.pk,
            self.other_post1.pk,
            self.other_repost0.pk,
            filter_on_stat=1,
            order_by='s.friends_reposts DESC',
        )

        # order by friend repost on minute 2
        self.assertResultEquals(
            self.friend_post0.pk,
            self.friend_post1.pk,
            self.other_post1.pk,
            self.other_repost0.pk,
            filter_on_stat=2,
            order_by='s.friends_reposts DESC',
        )

        # order by friend repost on minute 3
        self.assertResultEquals(
            self.friend_post0.pk,
            self.friend_post1.pk,
            self.other_post1.pk,
            self.other_repost0.pk,
            filter_on_stat=3,
            order_by='s.friends_reposts DESC',
        )

        # test_order_by_reposts on minute last
        self.assertResultEquals(
            self.friend_post0.pk,
            self.other_repost0.pk,
            self.other_post1.pk,
            self.friend_post1.pk,
            order_by='s.reposts DESC',
        )

        # test_order_by_reposts on minute 1
        self.assertResultEquals(
            self.friend_post1.pk,
            self.friend_post0.pk,
            self.other_repost0.pk,
            self.other_post1.pk,
            filter_on_stat=1,
            order_by='s.reposts DESC',
        )

        # test_order_by_reposts on minute 2
        self.assertResultEquals(
            self.other_post1.pk,
            self.friend_post1.pk,
            self.other_repost0.pk,
            self.friend_post0.pk,
            filter_on_stat=2,
            order_by='s.reposts DESC',
        )

        # test_order_by_reposts on minute 3
        self.assertResultEquals(
            self.friend_post0.pk,
            self.other_repost0.pk,
            self.other_post1.pk,
            self.friend_post1.pk,
            filter_on_stat=3,
            order_by='s.reposts DESC',
        )

        # test_order_by_reposts_per_followers_count
        self.assertResultEquals(
            self.friend_post0.pk,
            self.friend_post1.pk,
            self.other_repost0.pk,
            self.other_post1.pk,
            order_by='s.reposts_per_followers_count DESC',
        )

        # test_hub0
        self.assertResultEquals(
            self.friend_post0.pk,
            self.friend_post1.pk,
            hub=self.hub0.pk,
            order_by='s.reposts_per_followers_count DESC',
        )

        # test_hub1
        self.assertResultEquals(
            self.other_repost0.pk,
            self.other_post1.pk,
            hub=self.hub1.pk,
            order_by='s.reposts_per_followers_count DESC',
        )

        # test_kind1
        self.assertResultEquals(
            self.friend_post0.pk,
            kind=1,
            order_by='s.reposts_per_followers_count DESC',
        )

        # test_kind2
        self.assertResultEquals(
            self.friend_post1.pk,
            self.other_repost0.pk,
            kind=2,
            order_by='s.reposts_per_followers_count DESC',
        )

        # test_kind3
        self.assertResultEquals(
            self.other_post1.pk,
            kind=3,
            order_by='s.reposts_per_followers_count DESC',
        )
