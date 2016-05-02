import os

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from posts.models import Post, Poster

import pytz


class Command(BaseCommand):
    def handle(self, *args, **options):
        for poster in Poster.objects.all():
            recent_posts = poster.post_set.order_by('-datetime')
            best_posts = poster.post_set.order_by('-last_stat__reposts')

            posts = poster.post_set.exclude(
                pk__in=recent_posts.values_list('pk', flat=True)[:50]
            ).exclude(
                pk__in=best_posts.values_list('pk', flat=True)[:50]
            )

            print 'Would delete %s out of %s posts by %s' % (
                posts.count(),
                poster.post_set.count(),
                poster,
            )

            if posts.count():
                posts.delete()
