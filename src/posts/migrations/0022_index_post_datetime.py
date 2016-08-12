# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0021_force_poster_source'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='datetime',
            field=models.DateTimeField(db_index=True),
        ),
    ]
