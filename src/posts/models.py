from __future__ import unicode_literals

from datetime import datetime
from datetime import timedelta

import pytz

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import connection
from django.db import models
from django.utils import timezone


class PostManager(models.Manager):
    def posts_to_stat(self, from_minute, to_minute, now=None):
        posts = self.filter(parent=None)
        now = now or datetime.now(tz=pytz.utc)

        filters = None
        for i in range(from_minute, to_minute):
            kwargs = dict(
                datetime__gte=now - timedelta(
                    minutes=i,
                    seconds=10,
                ),
                datetime__lte=now - timedelta(
                    minutes=i,
                ) + timedelta(
                    seconds=10,
                ),
            )

            if not filters:
                filters = models.Q(**kwargs)
            else:
                filters |= models.Q(**kwargs)

        return posts.filter(filters).select_related(
            'poster',
            'last_stat',
        ).prefetch_related(
            'poster__average_set',
        )

    def filter_list(self, filter_on_stat=None, max_age_in_minutes=None,
            min_friends_reposts=None, min_average_compare=None, now=None,
            order_by=None):
        sql = '''
SELECT
    p.*,
    s.reposts,
    s.minute,
    s.speed,
    s.acceleration,
    s.reposts_per_followers_count,
    s.friends_reposts,
    s.total_posts as poster_total_posts,
    s.total_reposts as poster_total_reposts,
    s.average as poster_average,
    s.average_compare as average_compare,
    po.upstream_id as poster_upstream_id,
    po.name as poster_name,
    po.followers_count as poster_follower_count
FROM
    posts_post AS p
LEFT JOIN
    posts_poster AS po ON po.id = p.poster_id,
LATERAL
    (
        SELECT
            s.reposts,
            s.minute,
            s.speed,
            s.acceleration,
            s.reposts_per_followers_count,
            s.friends_reposts,
            pa.total_posts,
            pa.total_reposts,
            pa.average,
            (
                CASE WHEN pa.average = 0 THEN
                    0
                ELSE
                    s.reposts::float / pa.average
                END
            ) AS average_compare
        FROM
            posts_stat s
        LEFT JOIN
            posts_posteraveragestat pa ON pa.poster_id = p.poster_id AND pa.minute = s.minute
        WHERE
            post_id = p.id
            {lateral_where}
        ORDER BY
            minute DESC
        LIMIT 1
    ) AS s
WHERE
    {main_where}
ORDER BY
    {main_order_by}, p.id DESC
LIMIT 100
'''
        format_kwargs = {
            'lateral_where': '',
            'main_order_by': order_by or 'p.datetime DESC',
            'main_where': 'TRUE',
        }
        kwargs = {}

        if filter_on_stat and filter_on_stat != 'last':
            format_kwargs['lateral_where'] = ' AND s.minute = %(minute)s'
            kwargs['minute'] = int(filter_on_stat)

        if min_friends_reposts:
            format_kwargs['main_where'] += ' AND s.friends_reposts >= %(min_friends_reposts)s'
            kwargs['min_friends_reposts'] = min_friends_reposts

        if min_average_compare:
            format_kwargs['main_where'] += ' AND average_compare >= %(min_average_compare)s'
            kwargs['min_average_compare'] = min_average_compare

        if max_age_in_minutes:
            min_datetime = (now or datetime.now(tz=pytz.utc)) - timedelta(
                minutes=int(max_age_in_minutes)
            )
            format_kwargs['main_where'] += ' AND p.datetime >= %(min_datetime)s'
            kwargs['min_datetime'] = min_datetime

        cursor = connection.cursor()
        sql = sql.format(**format_kwargs)

        cursor.execute(sql, kwargs)
        columns = [col[0] for col in cursor.description]
        result = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

        if settings.DEBUG:
            print sql % kwargs
            import pprint
            pprint.pprint(result)

        return result

class Post(models.Model):
    upstream_id = models.BigIntegerField(db_index=True, unique=True)
    parent = models.ForeignKey(
        'self',
        related_name='children',
        null=True,
        blank=True
    )
    datetime = models.DateTimeField(db_index=True)
    added = models.DateTimeField(auto_now_add=True, db_index=True)
    poster = models.ForeignKey('Poster')
    content = models.TextField()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    source = GenericForeignKey('content_type', 'object_id')

    # Should be updated every time you add a stat
    last_stat = models.ForeignKey('Stat', null=True, related_name='last_of')

    objects = PostManager()

    def __unicode__(self):
        return u'#%s %s' % (self.id, self.content)

    def get_absolute_url(self):
        return reverse('posts:post_detail', args=(self.pk,))

    def minutes_since(self, now=None):
        now = now or datetime.now(tzinfo=pytz.utc)
        delta = now - self.datetime
        minute = delta.seconds / 60
        extra = delta.seconds % 60
        if extra >= 30:
            minute += 1
        return minute


class Poster(models.Model):
    upstream_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=150)
    followers_count = models.PositiveIntegerField()
    friend = models.BooleanField(default=False)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    source = GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return u'@%s' % self.name

    def get_absolute_url(self):
        return reverse('posts:poster_detail', args=(self.pk,))


class StatManager(models.Manager):
    def add_for_post(self, post, reposts, now):
        stat = Stat(
            post=post,
            reposts=reposts,
            reposts_per_followers_count=(
                reposts / (post.poster.followers_count or 1)
            ),
            minute=post.minutes_since(now),
            friends_reposts=Post.objects.filter(
                parent=post,
                poster__friend=True
            ).count() + (1 if post.poster.friend else 0)
        )

        if post.last_stat:
            stat.speed = reposts - post.last_stat.reposts
            stat.acceleration = stat.speed - post.last_stat.speed
        else:
            stat.speed = float(reposts) / (
                ((now - post.datetime).seconds / 60)
                or 1
            )
            stat.acceleration = stat.speed

        average = None
        for average in PosterAverageStat.objects.filter(poster=post.poster):
            if average.minute == stat.minute:
                break

        if average and average.minute == stat.minute:
            average.total_posts += 1
            average.total_reposts += stat.reposts
            average.average = float(average.total_reposts) / average.total_posts
        else:
            average = PosterAverageStat(
                poster=post.poster,
                minute=stat.minute,
                total_posts=1,
                total_reposts=stat.reposts,
                average=stat.reposts,
            )

        stat.save()
        Post.objects.filter(pk=post.pk).update(last_stat=stat)

        average.save()
        return stat

class Stat(models.Model):
    post = models.ForeignKey('Post')
    added = models.DateTimeField(default=timezone.now, db_index=True)
    reposts = models.PositiveIntegerField(db_index=True)
    minute = models.PositiveIntegerField(db_index=True)

    # Denormalized fields provisionned by trigger
    speed = models.FloatField(null=True, db_index=True)
    acceleration = models.FloatField(null=True, db_index=True)
    reposts_per_followers_count = models.FloatField(null=True, db_index=True)
    friends_reposts = models.PositiveIntegerField(default=0, db_index=True)

    objects = StatManager()

    class Meta:
        index_together = (
            ('post', 'minute'),
        )


class PosterAverageStat(models.Model):
    poster = models.ForeignKey('Poster', related_name='average_set')
    # Number of posts used to calculate the average
    total_posts = models.PositiveIntegerField()
    # Sum of reposts for all posts used so far
    total_reposts = models.PositiveIntegerField()
    # Stat taken at this minute
    minute = models.PositiveIntegerField(db_index=True)
    # total_reposts / total_posts
    average = models.FloatField(db_index=True)

    def __unicode__(self):
        return unicode(self.poster_id)

    class Meta:
        unique_together = (
            (
                'poster',
                'minute',
            ),
        )
