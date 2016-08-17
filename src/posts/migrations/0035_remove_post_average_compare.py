# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0034_drop_friends_reposts_trigger'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stat',
            name='average_compare',
        ),
    ]
