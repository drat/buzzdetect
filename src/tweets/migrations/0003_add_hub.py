# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0038_add_hub'),
        ('tweets', '0002_twitteraccount_follow'),
    ]

    operations = [
        migrations.AddField(
            model_name='twitteraccount',
            name='hub',
            field=models.ForeignKey(blank=True, to='posts.Hub', null=True),
        ),
    ]
