import feedparser
import requests
import threading
import pytz

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.template.defaultfilters import slugify

from posts.models import Post, Poster, Stat
from youtubes.models import YoutubeAccount, YoutubeAPIKey

import pytz


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.monitor()

    @staticmethod
    def update_channel(poster):
        now = datetime.now(tz=pytz.utc)
        result = feedparser.parse(
            'https://www.youtube.com/feeds/videos.xml?channel_id=%s'
            % poster.upstream_id,
        )

        for entry in result.get('entries', []):
            Command.update_post(poster, entry, now)

    @staticmethod
    def update_post(poster, entry, now):
        post, c = poster.post_set.get_or_create(
            upstream_id=entry.yt_videoid,
            datetime=entry.published,
            content=entry.summary,
            account=poster.accounts.all()[0],
            kind=3,  # video
        )

        views = int(entry.media_statistics['views'])
        if c:
            print 'Added post', post
            return Stat.objects.add_for_post(posts, views)

        # We want to update once per hour
        hours_since = post.minutes_since(now) / 60

        if hours_since == 0:
            return  # it's been less than an hour

        minute = hours_since * 60
        if post.stat_set.filter(minute=minute).count():
            return  # we already have a stat for this hour

        Stat.objects.add_for_post(
            post,
            views,
            # rounding the hour
            post.datetime + timedelta(hours=hours_since)
        )
        print 'Added stat for post', post

    @staticmethod
    def update_channels():
        with transaction.atomic():
            for account in YoutubeAccount.objects.all():
                account.sync()

        for channel in Poster.objects.exclude(accounts__youtubeaccount=None):
            Command.update_channel(channel)

        threading.Timer(
            20,
            Command.update_channels,
        ).start()

    @staticmethod
    def monitor():
        Command.update_channels()
