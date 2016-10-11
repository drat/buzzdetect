import requests

from django.db import models

from posts.models import Account, Poster


class YoutubeAPIKey(models.Model):
    api_key = models.CharField(max_length=100)

    def __unicode__(self):
        return self.api_key


class YoutubeAccount(Account):
    channel_id = models.CharField(max_length=100, unique=True)

    def sync(self, subscriptions=None):
        subscriptions = subscriptions or YoutubeRequest().get_items(
            'subscriptions',
            channelId=self.channel_id,
            part='contentDetails,snippet',
        )

        channel_ids = []
        for subscription in subscriptions:
            channel_id = subscription['snippet']['resourceId']['channelId']
            name = subscription['snippet']['title']
            followers_count = 0

            poster, c = Poster.objects.get_or_create(
                upstream_id=channel_id,
                name=name,
                friend=True,
                followers_count=followers_count,
            )
            poster.accounts.add(self)
            channel_ids.append(channel_id)

        for p in self.poster_set.exclude(upstream_id__in=channel_ids):
            p.accounts.remove(self)


class YoutubeRequest(object):
    def get(self, endpoint, **params):
        for key in YoutubeAPIKey.objects.all():
            params['key'] = key.api_key

            try:
                return self._get(endpoint, params)
            except:
                continue

    def _get(self, endpoint, params):
        url = 'https://www.googleapis.com/youtube/v3/' + endpoint
        return requests.get(url, params=params)

    def get_items(self, endpoint, **params):
        params.setdefault('resultsPerPage', 50)
        response = self.get(endpoint, **params)
        data = response.json()

        for i in data.get('items', []):
            yield i

        while 'nextPageToken' in data:
            params['pageToken'] = data['nextPageToken']
            response = self.get(endpoint, **params)
            data = response.json()
            for i in data.get('items', []):
                yield i
