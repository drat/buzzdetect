from datetime import datetime, timedelta

from django.core.cache import cache
from django.db.models import Prefetch
from django.views import generic

import pytz

from .forms import PostSearchForm
from .models import Post, Poster, Stat


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
        from tweets.utils import get_twitter
        if data is None:
            data = get_twitter().users.show(_id=self.object.upstream_id)
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


class PostList(generic.ListView):
    model = Post
    template_name = 'posts/post_list.html'

    def get_queryset(self):
        q = super(PostList, self).get_queryset()

        order_by = self.request.GET.get('order_by', 'friends_reposts')
        filter_on_stat = self.request.GET.get('filter_on_stat', 'current')
        max_age_in_minutes = self.request.GET.get('max_age_in_minutes', '30')
        min_friends_reposts = self.request.GET.get('min_friends_reposts', '2')

        posts = Post.objects.filter(
            datetime__gte=datetime.now(tz=pytz.utc) - timedelta(
                minutes=int(max_age_in_minutes)
            ),
        )

        if filter_on_stat == 'current':
            stat = 'last_stat'
        elif filter_on_stat == '2 minutes':
            stat = 'stat_after_two_minute'

        if min_friends_reposts:
            posts = posts.filter(**{
                '%s__friends_reposts__gte' % stat: min_friends_reposts
            })

        q = posts.select_related(
            'poster',
            'last_stat',
            'stat_after_two_minute',
        ).order_by(
            '-%s__%s' % (stat, order_by)
        )[:30]

        return q

    def get_context_data(self, *args, **kwargs):
        c = super(PostList, self).get_context_data(*args, **kwargs)
        c['form'] = PostSearchForm(self.request.GET or None)
        return c