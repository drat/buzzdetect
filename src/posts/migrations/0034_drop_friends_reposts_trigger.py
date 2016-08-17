# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
TRIGGER = '''
DROP TRIGGER IF EXISTS update_parent_friends_reposts  ON post_post;
DROP FUNCTION IF EXISTS update_parent_friends_reposts() CASCADE;
'''


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0033_add_stat_average_compare'),
    ]

    operations = [
        migrations.RunSQL(TRIGGER),
    ]
