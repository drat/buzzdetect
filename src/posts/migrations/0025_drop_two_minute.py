# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

TRIGGER = '''
DROP TRIGGER IF EXISTS update_stat_after_two_minutes ON post_stat;
DROP FUNCTION IF EXISTS update_stat_after_two_minutes() CASCADE;
'''


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0024_average_compare_division_by_zero_fix'),
    ]

    operations = [
        migrations.RunSQL(TRIGGER),
        migrations.RemoveField(
            model_name='post',
            name='stat_after_two_minute',
        ),
        migrations.RemoveField(
            model_name='poster',
            name='average_after_two_minute',
        ),
    ]
