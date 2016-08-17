from __future__ import unicode_literals

from django.db import migrations, models

TRIGGER = '''
DROP TRIGGER IF EXISTS update_poster_average_after_three_minute ON posts_posteraveragestat;
DROP FUNCTION IF EXISTS update_poster_average_after_three_minute() CASCADE;
'''


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0031_stat_minutes_to_stat_minute'),
    ]

    operations = [
        migrations.RunSQL(TRIGGER),
    ]
