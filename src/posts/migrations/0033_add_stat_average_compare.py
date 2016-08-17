# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0032_drop_update_poster_average_after_three_minute_trigger'),
    ]

    operations = [
        migrations.AddField(
            model_name='stat',
            name='average_compare',
            field=models.FloatField(null=True, db_index=True),
        ),
    ]
