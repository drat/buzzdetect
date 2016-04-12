from datetime import datetime, timedelta

from django.db.models import Prefetch
from django.views import generic

import pytz

from .models import Tweet


class TweetList(generic.TemplateView):
    model = Tweet
    template_name = 'tweets/tweet_list.html'

    def get_context_data(self, *args, **kwargs):
        c = super(TweetList, self).get_context_data(*args, **kwargs)

        c['min_datetime'] = (
            datetime.now(tz=pytz.utc)
            - timedelta(minutes=30)
        )

        c['min_friends_retweets'] = int(self.request.GET.get('min', 2))

        c['tweets'] = Tweet.objects.filter(
            friends_retweets__gte=c['min_friends_retweets'],
            parent=None,
        ).select_related(
            'source',
            'last_retweets',
        )

        if not self.request.GET.get('anytime', None):
            c['tweets'] = c['tweets'].filter(
                datetime__gte=c['min_datetime'],
            )

        c['tweets'] = c['tweets'].order_by(
            '-friends_retweets',
            '-last_retweets__acceleration',
        )

        return c
