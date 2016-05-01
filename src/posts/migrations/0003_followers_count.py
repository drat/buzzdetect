# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_stat_speed_acceleration'),
    ]

    operations = [
        migrations.AddField(
            model_name='poster',
            name='followers_count',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
