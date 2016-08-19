import os

from django.db import models

from posts.models import Account

from twitter import OAuth
from twitter import Twitter
from twitter.api import TwitterHTTPError


class TwitterAccount(Account):
    consumer_key = models.CharField(max_length=255)
    consumer_secret = models.CharField(max_length=255)
    token = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)

    def get_oauth(self):
        if not getattr(self, '_oauth', None):
            self._oauth = OAuth(
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret,
                token=self.token,
                token_secret=self.secret,
            )

        return self._oauth

    def get_twitter(self):
        if not getattr(self, '_twitter', None):
            self._twitter = Twitter(auth=self.get_oauth())
        return self._twitter

    def get_data(self, status_id):
        try:
            return self.get_twitter().statuses.show(_id=status_id)
        except TwitterHTTPError as e:
            if 'Twitter sent status 404 for URL' in e.message:
                return 'deleted'
            return None

    def get_source_data(self, twitter_id):
        return self.get_twitter().users.show(_id=twitter_id)
