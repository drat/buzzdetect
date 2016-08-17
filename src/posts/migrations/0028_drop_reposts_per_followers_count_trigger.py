# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

TRIGGER = '''
DROP TRIGGER IF EXISTS calculate_reposts_per_followers_count ON post_stat;
DROP FUNCTION IF EXISTS get_reposts_per_followers_count() CASCADE;
'''


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0027_drop_stat_speed_acceleration_trigger'),
    ]

    operations = [
        migrations.RunSQL(TRIGGER),
    ]
