# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import subprocess

from django.db import migrations, models


def check_processes(apps, schema_editor):
    try:
        subprocess.check_call('pgrep -f twitter_', shell=True)
    except subprocess.CalledProcessError:
        return True
    else:
        raise Exception(
            'Please stop all buzzdetect processes before this migration'
        )


def check_source_required(apps, schema_editor):
    Post = apps.get_model('posts', 'Post')

    if Post.objects.count() == 0:
        return True

    if not os.getenv('TWITTER_CONSUMER_KEY'):
        raise Exception(
            'This migration requires TWITTER_* environment variables if the'
            'post table is not empty'
        )


def set_source(apps, schema_editor):
    Post = apps.get_model('posts', 'Post')

    if Post.objects.count() == 0:
        return True

    ContentType = apps.get_model('contenttypes', 'ContentType')
    TwitterAccount = apps.get_model('tweets', 'TwitterAccount')

    account, created = TwitterAccount.objects.get_or_create(
        consumer_key=os.environ['TWITTER_CONSUMER_KEY'],
        consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'],
        token=os.environ['TWITTER_TOKEN'],
        secret=os.environ['TWITTER_TOKEN_SECRET'],
    )

    Post.objects.all().update(
        content_type=ContentType.objects.get_for_model(account),
        object_id=account.pk,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0016_add_source'),
    ]

    operations = [
        migrations.RunPython(check_processes),
        migrations.RunPython(check_source_required),
        migrations.RunPython(set_source),
    ]
