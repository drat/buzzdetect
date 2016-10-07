# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-07 12:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0041_add_hub_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='kind',
            field=models.IntegerField(choices=[(1, 'Text'), (2, 'Photo'), (3, 'Video')], default=1),
        ),
    ]
