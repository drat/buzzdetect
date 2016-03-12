import os

from twitter import OAuth


def get_auth():
    return OAuth(
        consumer_key=os.environ.get('TWITTER_CONSUMER_KEY'),
        consumer_secret=os.environ.get('TWITTER_CONSUMER_SECRET'),
        token=os.environ.get('TWITTER_TOKEN'),
        token_secret=os.environ.get('TWITTER_TOKEN_SECRET'),
    )
