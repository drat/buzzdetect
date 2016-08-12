# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('posts', '0015_add_average_compare_after_three_minute'),
        ('tweets', '0002_twitteraccount_follow'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='object_id',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
