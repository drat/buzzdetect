from django.views import generic

from .models import Retweets, Tweet


class TweetList(generic.TemplateView):
    model = Tweet
    template_name = 'tweets/tweet_list.html'

    def get_context_data(self, *args, **kwargs):
        c = super(TweetList, self).get_context_data(*args, **kwargs)
        c['retweets'] = Retweets.objects.select_related('tweet').order_by(
            'tweet', 'acceleration').distinct('tweet')
        return c
