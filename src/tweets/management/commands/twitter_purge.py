from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from tweets.models import Tweet, Retweets
from tweets.utils import get_data

import pytz


class Command(BaseCommand):
    def handle(self, *args, **options):
        min_datetime = (
            datetime.now(tz=pytz.utc)
            - timedelta(hours=10)
        )

        old = Tweet.objects.filter(
            datetime__lte=min_datetime,
        )

        print 'Deleting %s old tweets' % old.count()

        old.delete()
