# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TwitterAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('consumer_key', models.CharField(max_length=255)),
                ('consumer_secret', models.CharField(max_length=255)),
                ('token', models.CharField(max_length=255)),
                ('secret', models.CharField(max_length=255)),
            ],
        ),
    ]
