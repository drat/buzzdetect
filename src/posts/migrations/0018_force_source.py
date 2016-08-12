# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0017_set_source'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='post',
            name='object_id',
            field=models.PositiveIntegerField(),
        ),
    ]
