# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0025_drop_two_minute'),
    ]

    operations = [
        migrations.AddField(
            model_name='stat',
            name='minutes',
            field=models.PositiveIntegerField(default=0, db_index=True),
            preserve_default=False,
        ),
    ]
