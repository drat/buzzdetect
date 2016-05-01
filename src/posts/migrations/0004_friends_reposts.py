# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

TRIGGER = '''
CREATE OR REPLACE FUNCTION update_parent_friends_reposts()
RETURNS trigger
AS $$
    BEGIN
        IF
            NEW.parent_id IS NOT NULL
        THEN
            UPDATE
                posts_post
            SET
                friends_reposts = (
                    SELECT
                        COUNT(friends_posts.id)
                    FROM
                        posts_post AS friends_posts
                    WHERE
                        friends_posts.parent_id=NEW.parent_id
                )
            WHERE
                posts_post.id = NEW.parent_id
            ;
        END IF;
        RETURN NEW;
    END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER update_parent_friends_reposts
AFTER INSERT ON posts_post
FOR EACH ROW EXECUTE PROCEDURE update_parent_friends_reposts();
'''


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_followers_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='friends_reposts',
            field=models.PositiveIntegerField(default=0, db_index=True),
        ),
        migrations.RunSQL(TRIGGER)
    ]
