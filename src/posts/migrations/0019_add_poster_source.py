# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('posts', '0018_force_source'),
    ]

    operations = [
        migrations.AddField(
            model_name='poster',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='poster',
            name='object_id',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
