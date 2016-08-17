# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0030_drop_most_code'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stat',
            old_name='minutes',
            new_name='minute',
        ),
    ]
