from django.conf.urls import url

import views

app_name = 'posts'

urlpatterns = [
    url(
        r'^poster/(?P<pk>\d+)/$',
        views.PosterDetail.as_view(),
        name='poster_detail',
    ),
    url(
        r'^post/(?P<pk>\d+)/$',
        views.PostDetail.as_view(),
        name='post_detail',
    ),
    url(
        r'^$',
        views.PostList.as_view(),
        name='post_list',
    ),
]
