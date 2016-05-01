# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('upstream_id', models.BigIntegerField(unique=True, db_index=True)),
                ('datetime', models.DateTimeField()),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField()),
                ('parent', models.ForeignKey(related_name='children', blank=True, to='posts.Post', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Poster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('upstream_id', models.BigIntegerField(unique=True)),
                ('name', models.CharField(max_length=150)),
                ('friend', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Stat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('reposts', models.PositiveIntegerField()),
                ('post', models.ForeignKey(to='posts.Post')),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='poster',
            field=models.ForeignKey(to='posts.Poster'),
        ),
    ]
