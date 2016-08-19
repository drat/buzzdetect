# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0038_add_hub'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('follow', models.BooleanField(default=True)),
                ('hub', models.ForeignKey(blank=True, to='posts.Hub', null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='post',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='post',
            name='object_id',
        ),
        migrations.RemoveField(
            model_name='poster',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='poster',
            name='hubs',
        ),
        migrations.RemoveField(
            model_name='poster',
            name='object_id',
        ),
        migrations.AddField(
            model_name='poster',
            name='accounts',
            field=models.ManyToManyField(to='posts.Account'),
        ),
    ]
