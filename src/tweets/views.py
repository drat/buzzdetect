from datetime import datetime, timedelta

from django.views import generic

import pytz

from .models import Retweets, Tweet


class TweetList(generic.TemplateView):
    model = Tweet
    template_name = 'tweets/tweet_list.html'

    def get_context_data(self, *args, **kwargs):
        c = super(TweetList, self).get_context_data(*args, **kwargs)

        min_datetime = datetime.utcnow() - timedelta(minutes=20)

        retweets = Retweets.objects.filter(
            datetime__gte=min_datetime,
        ).exclude(
            acceleration=0
        ).order_by(
            'tweet',
        ).distinct(
            'tweet'
        )

        c['retweets'] = Retweets.objects.filter(
            pk__in=retweets.values_list('pk'),
        ).select_related(
            'tweet'
        ).order_by(
            '-acceleration'
        )

        for r in c['retweets']:
            delta = datetime.now(pytz.utc) - r.tweet.datetime
            minutes = delta.seconds / 60.0
            r.total_retweet_per_minute = r.retweet_count / minutes

        return c
