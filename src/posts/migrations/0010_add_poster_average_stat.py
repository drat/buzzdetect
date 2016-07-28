# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-19 13:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_stat_friends_repost_include_children'),
    ]

    operations = [
        migrations.CreateModel(
            name='PosterAverageStat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_posts', models.PositiveIntegerField()),
                ('total_reposts', models.PositiveIntegerField()),
                ('seconds', models.PositiveIntegerField(db_index=True)),
                ('average', models.FloatField(db_index=True)),
                ('poster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='posts.Poster')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='posteraveragestat',
            unique_together=set([('poster', 'seconds')]),
        ),
    ]