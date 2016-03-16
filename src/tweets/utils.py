import os

from twitter import OAuth
from twitter import Twitter
from twitter.api import TwitterHTTPError

oauth = None
twitter = None


def get_auth():
    global oauth

    if oauth is None:
        oauth = OAuth(
            consumer_key=os.environ.get('TWITTER_CONSUMER_KEY'),
            consumer_secret=os.environ.get('TWITTER_CONSUMER_SECRET'),
            token=os.environ.get('TWITTER_TOKEN'),
            token_secret=os.environ.get('TWITTER_TOKEN_SECRET'),
        )

    return oauth


def get_data(status_id):
    global twitter

    if twitter is None:
        twitter = Twitter(auth=get_auth())

    try:
        return twitter.statuses.show(_id=status_id)
    except TwitterHTTPError as e:
        print e
        return None
