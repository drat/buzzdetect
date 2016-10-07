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
    if not os.getenv('CI'):
        raise Exception(
            'Please stop all buzzdetect processes before this migration'
        )


def set_poster_source(apps, schema_editor):
    Poster = apps.get_model('posts', 'Poster')

    if Poster.objects.count() == 0:
        return True

    ContentType = apps.get_model('contenttypes', 'ContentType')
    TwitterAccount = apps.get_model('tweets', 'TwitterAccount')
    account = TwitterAccount.objects.first()

    Poster.objects.all().update(
        content_type=ContentType.objects.get_for_model(account),
        object_id=account.pk,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0019_add_poster_source'),
    ]

    operations = [
        migrations.RunPython(check_processes),
        migrations.RunPython(set_poster_source),
    ]
