# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-12 14:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Retweets',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('retweet_count', models.PositiveIntegerField(db_index=True, default=0)),
                ('retweet_per_minute', models.FloatField(db_index=True, default=0)),
                ('acceleration', models.FloatField(db_index=True, default=0)),
            ],
            options={
                'ordering': ('acceleration',),
            },
        ),
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=180)),
                ('twitter_id', models.BigIntegerField()),
                ('datetime', models.DateTimeField()),
            ],
        ),
        migrations.AddField(
            model_name='retweets',
            name='tweet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tweets.Tweet'),
        ),
        migrations.AlterUniqueTogether(
            name='retweets',
            unique_together=set([('datetime', 'tweet')]),
        ),
    ]
