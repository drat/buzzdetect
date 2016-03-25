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


def get_twitter():
    global twitter

    if twitter is None:
        twitter = Twitter(auth=get_auth())

    return twitter


def get_data(status_id):
    twitter = get_twitter()

    try:
        return twitter.statuses.show(_id=status_id)
    except TwitterHTTPError as e:
        if 'Twitter sent status 404 for URL' in e.message:
            return 'deleted'
        return None


def get_source_data(twitter_id):
    twitter = get_twitter()

    return twitter.users.show(_id=twitter_id)
