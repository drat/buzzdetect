from django.conf.urls import url

from .views import TweetList

app_name = 'tweets'


urlpatterns = [
    url(
        r'^$',
        TweetList.as_view(),
        name='tweet_list',
    ),
]
