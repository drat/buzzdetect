from datetime import datetime, timedelta

from django.core.cache import cache
from django.db.models import Prefetch
from django.views import generic

import pytz

from .forms import PostSearchForm
from .models import Hub, Post, Poster, Stat


class PosterDetail(generic.DetailView):
    model = Poster
    show_data = [
        'name',
        'screen_name',
        'description',
        'followers_count',
        'following',
        'created_at',
        'friends_count',
        'lang',
        'location',
        'time_zone',
        'statuses_count',
    ]

    def get_context_data(self, *args, **kwargs):
        c = super(PosterDetail, self).get_context_data(*args, **kwargs)

        key = 'poster_%s' % self.object.pk
        data = cache.get(key)
        if data is None:
            data = self.object.source.get_twitter().users.show(
                _id=self.object.upstream_id
            )
            cache.set(key, data, 3600*12)
        c['data'] = data

        c['table'] = [
            (k, data[k]) for k in self.show_data
        ]
        print c['table']

        return c

class PostDetail(generic.DetailView):
    model = Post

    def get_queryset(self):
        return Post.objects.prefetch_related(
            Prefetch(
                'children',
                queryset=Post.objects.select_related('poster'),
            ),
            Prefetch(
                'stat_set',
                queryset=Stat.objects.order_by('added'),
            ),
        ).select_related(
            'parent__poster',
            'poster',
        )


class PostList(generic.TemplateView):
    model = Post
    template_name = 'posts/post_list.html'

    def get_context_data(self, *args, **kwargs):
        c = super(PostList, self).get_context_data(*args, **kwargs)
        c['form'], c['results'] = PostSearchForm.post_list(
            self.request.user,
            self.request.GET
        )
        ids = [r['id'] for r in c['results']]

        c['posts'] = list(
            Post.objects.filter(
                pk__in=[r['id'] for r in c['results']],
            ).select_related('poster').prefetch_related('stat_set')
        )
        c['posts'].sort(key=lambda p: ids.index(p.pk))
        return c
