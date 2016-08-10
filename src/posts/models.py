from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone


class Post(models.Model):
    upstream_id = models.BigIntegerField(db_index=True, unique=True)
    parent = models.ForeignKey(
        'self',
        related_name='children',
        null=True,
        blank=True
    )
    datetime = models.DateTimeField()
    added = models.DateTimeField(auto_now_add=True)
    poster = models.ForeignKey('Poster')
    content = models.TextField()

    # Denormalized field handled by trigger
    last_stat = models.ForeignKey('Stat', null=True, related_name='last_of')

    # Denormalized field handled by trigger
    stat_after_two_minute = models.ForeignKey(
        'Stat',
        db_index=True,
        null=True,
        related_name='two_minute_for'
    )
    stat_after_three_minute = models.ForeignKey(
        'Stat',
        db_index=True,
        null=True,
        related_name='three_minute_for'
    )

    def __unicode__(self):
        return u'#%s %s' % (self.id, self.content)

    def get_absolute_url(self):
        return reverse('posts:post_detail', args=(self.pk,))


class Poster(models.Model):
    upstream_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=150)
    followers_count = models.PositiveIntegerField()
    friend = models.BooleanField(default=False)

    # Denormalized field handled by trigger
    average_after_two_minute = models.ForeignKey(
        'PosterAverageStat',
        db_index=True,
        null=True,
        related_name='two_minute_for'
    )
    average_after_three_minute = models.ForeignKey(
        'PosterAverageStat',
        db_index=True,
        null=True,
        related_name='three_minute_for'
    )

    def __unicode__(self):
        return u'@%s' % self.name

    def get_absolute_url(self):
        return reverse('posts:poster_detail', args=(self.pk,))


class Stat(models.Model):
    post = models.ForeignKey('Post')
    added = models.DateTimeField(default=timezone.now)
    reposts = models.PositiveIntegerField()

    # Denormalized fields provisionned by trigger
    speed = models.FloatField(null=True, db_index=True)
    acceleration = models.FloatField(null=True, db_index=True)
    reposts_per_followers_count = models.FloatField(null=True, db_index=True)
    friends_reposts = models.PositiveIntegerField(default=0, db_index=True)


class PosterAverageStat(models.Model):
    poster = models.ForeignKey('Poster', related_name='average_set')
    # Number of posts used to calculate the average
    total_posts = models.PositiveIntegerField()
    # Sum of reposts for all posts used so far
    total_reposts = models.PositiveIntegerField()
    # Flattened time in seconds, ie. 120 for stat_after_two_minute
    seconds = models.PositiveIntegerField(db_index=True)
    # total_reposts / total_posts
    average = models.FloatField(db_index=True)

    class Meta:
        unique_together = (
            (
                'poster',
                'seconds',
            ),
        )
