# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

TRIGGER = '''
CREATE OR REPLACE FUNCTION update_poster_average_after_three_minute()
RETURNS trigger
AS $$
    BEGIN
        IF
            NEW.seconds = 180
        THEN
            UPDATE
                posts_poster
            SET
                average_after_three_minute_id = NEW.id
            WHERE
                posts_poster.id = NEW.poster_id;
        END IF;
        RETURN NEW;
    END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER update_poster_average_after_three_minute
AFTER INSERT ON posts_posteraveragestat
FOR EACH ROW EXECUTE PROCEDURE update_poster_average_after_three_minute();

CREATE OR REPLACE FUNCTION update_stat_after_three_minute()
RETURNS trigger
AS $$
    DECLARE post posts_post%ROWTYPE;
    DECLARE posteraveragestat posts_posteraveragestat%ROWTYPE;
    DECLARE new_posteraveragestat posts_posteraveragestat%ROWTYPE;
    BEGIN
        RAISE LOG '3 minute trigger % % %', NEW.reposts, NEW.post_id, NEW.added;
        -- Get the post's datetime, stat_after_three_minute and poster_id for
        -- this stat
        SELECT
            *
        FROM
            posts_post
        WHERE
            id = NEW.post_id
        INTO post;

        -- If we don't want this stat as stat_after_three_minute then we have
        -- nothing else to do
        RAISE LOG 'Has % secs', extract('epoch' from NEW.added - post.datetime);
        IF
            extract('epoch' from NEW.added - post.datetime) < 180
        OR
            extract('epoch' from NEW.added - post.datetime) > 195
        THEN
            RAISE LOG 'Not retaining for 3 minute trigger';
            RETURN NEW;
        END IF;
        RAISE LOG 'Retaining for 3 minute trigger';

        -- If the posts already has stat_after_three_minute then we have nothing
        -- to do
        IF
            post.stat_after_three_minute_id IS NOT NULL
        THEN
            RETURN NEW;
        END IF;

        -- Get the current total posts, reposts and average after three minute
        -- for this stats post poster
        SELECT
            *
        FROM
            posts_posteraveragestat
        WHERE
            poster_id = post.poster_id
        AND
            seconds = 180
        INTO
            posteraveragestat;

        -- Calculate the new total posts, reposts and average after three minute
        -- for this stats post poster, otherwise get started with this stat
        IF
            posteraveragestat.total_posts IS NULL
        THEN
            SELECT
                nextval(pg_get_serial_sequence('posts_posteraveragestat', 'id')),
                1 AS total_posts,
                NEW.reposts AS total_reposts,
                180 AS seconds,
                NEW.reposts AS average,
                post.poster_id AS poster_id
            INTO new_posteraveragestat;
            RAISE LOG 'Creating new stat';
        ELSE
            SELECT
                nextval(pg_get_serial_sequence('posts_posteraveragestat', 'id')),
                posteraveragestat.total_posts + 1 AS total_posts,
                posteraveragestat.total_reposts + NEW.reposts AS total_reposts,
                180 AS seconds,
                (
                    (
                        posteraveragestat.total_reposts + NEW.reposts
                    )
                    /
                    (
                        posteraveragestat.total_posts + 1
                    )
                )
                AS average,
                post.poster_id AS poster_id
            INTO new_posteraveragestat;
            RAISE LOG 'Calculating stat';
        END IF;

        -- Insert or update the average after three minute
        INSERT INTO
            posts_posteraveragestat
        VALUES (
            new_posteraveragestat.*
        )
        ON CONFLICT (poster_id, seconds) DO UPDATE SET
            poster_id = new_posteraveragestat.poster_id,
            seconds = new_posteraveragestat.seconds,
            total_posts = new_posteraveragestat.total_posts,
            total_reposts = new_posteraveragestat.total_reposts,
            average = new_posteraveragestat.average
        ;
        RAISE LOG 'Updated stat to % % % for %', new_posteraveragestat.total_reposts, new_posteraveragestat.total_posts, new_posteraveragestat.average, new_posteraveragestat.poster_id;

        -- We may now reference to this stat as stat_after_three_minute
        UPDATE
            posts_post
        SET
            stat_after_three_minute_id = NEW.id
        WHERE
            id = NEW.post_id;
        RETURN NEW;
    END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER update_stat_after_three_minute
AFTER INSERT ON posts_stat
FOR EACH ROW EXECUTE PROCEDURE update_stat_after_three_minute();
'''


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0013_poster_average_after_two_minute'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='stat_after_three_minute',
            field=models.ForeignKey(related_name='three_minute_for', to='posts.Stat', null=True),
        ),
        migrations.AddField(
            model_name='poster',
            name='average_after_three_minute',
            field=models.ForeignKey(related_name='three_minute_for', to='posts.PosterAverageStat', null=True),
        ),
        migrations.RunSQL(TRIGGER),
    ]
