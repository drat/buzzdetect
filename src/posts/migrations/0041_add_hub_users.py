# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-07 09:55
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0040_add_post_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='hub',
            name='users',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
