from datetime import datetime, timedelta

from django.views import generic

import pytz

from .models import Retweets, Tweet


class TweetList(generic.TemplateView):
    model = Tweet
    template_name = 'tweets/tweet_list.html'

    def get_context_data(self, *args, **kwargs):
        c = super(TweetList, self).get_context_data(*args, **kwargs)

        c['tweets'] = Tweet.objects.exclude(total_rtm=None).order_by('-total_rtm')

        return c
