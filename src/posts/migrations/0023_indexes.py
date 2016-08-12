# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0022_index_post_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='added',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='average_compare_after_three_minute',
            field=models.FloatField(null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='stat',
            name='added',
            field=models.DateTimeField(default=django.utils.timezone.now, db_index=True),
        ),
        migrations.AlterField(
            model_name='stat',
            name='reposts',
            field=models.PositiveIntegerField(db_index=True),
        ),
    ]
