# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0035_remove_post_average_compare'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='stat',
            index_together=set([('post', 'minute')]),
        ),
    ]
