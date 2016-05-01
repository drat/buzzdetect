# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

TRIGGER = '''
CREATE OR REPLACE FUNCTION get_speed_and_acceleration()
RETURNS trigger
AS $$
    DECLARE last_stat posts_stat%ROWTYPE;
    BEGIN
        SELECT
            *
        FROM
            posts_stat
        WHERE
            post_id = NEW.post_id
        ORDER BY
            added DESC
        LIMIT 1
        INTO last_stat;

        SELECT
            (
                NEW.reposts - last_stat.reposts
            )
            /
            extract(
                'epoch' from NEW.added - last_stat.added
            )
        INTO NEW.speed;
        SELECT
            NEW.speed - last_stat.speed
        INTO NEW.acceleration;
        RETURN NEW;
    END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER calculate_speed_and_acceleration
BEFORE INSERT ON posts_stat
FOR EACH ROW EXECUTE PROCEDURE get_speed_and_acceleration();
'''

class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stat',
            name='acceleration',
            field=models.FloatField(null=True, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stat',
            name='speed',
            field=models.FloatField(null=True, db_index=True),
            preserve_default=False,
        ),
        migrations.RunSQL(TRIGGER)
    ]
