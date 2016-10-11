import random
import string


def random_string(length):
    return ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(length)
    )


def make_subscription(title):
    return {
        'kind': 'youtube#subscription',
        'etag': 'etag_' + random_string(50),
        'id': 'id_' + random_string(40),
        'snippet': {
            'publishedAt': '2016-03-28T12:51:28.000Z',
            'title': title,
            'description': 'hello !',
            'resourceId': {
                'kind': 'youtube#channel',
                'channelId': 'channelId_' + random_string(30),
            },
            'channelId': 'yourChannelId',
        },
        'contentDetails': {
            'totalItemCount': 545,
            'newItemCount': 0,
            'activityType': 'all'
        }
    }

def make_subscription_response(self, resultsPerPage=None, *items):
    return {
        'kind': 'youtube#subscriptionListResponse',
        'etag': 'etag_' + random_string(50),
        'nextPageToken': 'nextPageToken' + random_string(10),
        'pageInfo': {
            'totalResults': len(items),
            'resultsPerPage': resultsPerPage or 5,
        },
        'items': items
    }

