# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

TRIGGER = '''
DROP TRIGGER IF EXISTS update_poster_average_after_two_minute ON post_stat;
DROP FUNCTION IF EXISTS update_poster_average_after_two_minute() CASCADE;
'''


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0029_drop_last_stat_trigger'),
    ]

    operations = [
        migrations.RunSQL(TRIGGER),
        migrations.RemoveField(
            model_name='post',
            name='average_compare_after_three_minute',
        ),
        migrations.RemoveField(
            model_name='post',
            name='stat_after_three_minute',
        ),
        migrations.RemoveField(
            model_name='poster',
            name='average_after_three_minute',
        ),
        migrations.AddField(
            model_name='posteraveragestat',
            name='minute',
            field=models.PositiveIntegerField(default=0, db_index=True),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='posteraveragestat',
            unique_together=set([('poster', 'minute')]),
        ),
        migrations.RemoveField(
            model_name='posteraveragestat',
            name='seconds',
        ),
    ]
