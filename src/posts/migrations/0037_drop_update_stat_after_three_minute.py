# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

TRIGGER = '''
DROP TRIGGER IF EXISTS update_stat_after_three_minute ON post_stat;
DROP FUNCTION IF EXISTS update_stat_after_three_minute() CASCADE;
'''


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0036_index_stat_minute_poster_together'),
    ]

    operations = [
        migrations.RunSQL(TRIGGER),
    ]
