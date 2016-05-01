# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-01 22:12
from __future__ import unicode_literals

from django.db import migrations, models

TRIGGER = '''
CREATE OR REPLACE FUNCTION get_reposts_per_followers_count()
RETURNS trigger
AS $$
    DECLARE followers_count int;
    BEGIN
        SELECT
            posts_poster.followers_count
        FROM
            posts_post
        LEFT JOIN
            posts_poster ON posts_poster.id = posts_post.poster_id
        WHERE
            posts_post.id = NEW.post_id
        INTO followers_count;

        IF
            followers_count > 0
        THEN
            SELECT
                CAST(NEW.reposts AS float ) / followers_count
            INTO NEW.reposts_per_followers_count;
        END IF;

        RETURN NEW;
    END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER calculate_reposts_per_followers_count
BEFORE INSERT ON posts_stat
FOR EACH ROW EXECUTE PROCEDURE get_reposts_per_followers_count();
'''


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_friends_reposts'),
    ]

    operations = [
        migrations.AddField(
            model_name='stat',
            name='reposts_per_followers_count',
            field=models.FloatField(db_index=True, null=True),
        ),
        migrations.RunSQL(TRIGGER),
    ]
