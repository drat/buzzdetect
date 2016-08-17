# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

TRIGGER = '''
DROP TRIGGER IF EXISTS calculate_speed_and_acceleration ON post_stat;
DROP FUNCTION IF EXISTS get_speed_and_acceleration() CASCADE;
'''


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0026_stat_minute'),
    ]

    operations = [
        migrations.RunSQL(TRIGGER),
    ]
