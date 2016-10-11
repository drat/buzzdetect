from django import test

from posts.models import Poster
from youtubes.test import make_subscription
from youtubes.models import YoutubeAccount


class YoutubeAccountSyncTest(test.TransactionTestCase):
    def test_sync(self):
        Poster.objects.all().delete()

        account = YoutubeAccount.objects.create(
            name=self.id(),
            channel_id=self.id()
        )

        sub0 = make_subscription('sub0')
        sub1 = make_subscription('sub1')
        sub2 = make_subscription('sub2')


        account.sync([sub0, sub1])

        assert Poster.objects.count() == 2
        p0, p1 = Poster.objects.all().order_by('pk')
        assert [p0, p1] == list(account.poster_set.all())

        account.sync([
            sub1,
            sub2,
        ])

        p2 = Poster.objects.all().order_by('-pk')[0]
        assert [p1, p2] == list(account.poster_set.all())
