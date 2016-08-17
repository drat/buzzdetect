# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


TRIGGER = '''
DROP TRIGGER IF EXISTS update_last_stat ON post_stat;
DROP FUNCTION IF EXISTS get_last_stat() CASCADE;
'''


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0028_drop_reposts_per_followers_count_trigger'),
    ]

    operations = [
        migrations.RunSQL(TRIGGER),
    ]
