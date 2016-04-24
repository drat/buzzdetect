# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tweets', '0002_tweet_last_retweets'),
    ]

    operations = [
        migrations.AddField(
            model_name='retweets',
            name='seconds_after_tweet',
            field=models.PositiveIntegerField(default=None, null=True, db_index=True),
        ),
    ]
