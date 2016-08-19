# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0039_account_inheritance'),
        ('tweets', '0004_account_inheritance_create_account'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='twitteraccount',
            name='id',
        ),
        migrations.AddField(
            model_name='twitteraccount',
            name='account_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, null=True, serialize=False, to='posts.Account'),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='twitteraccount',
            name='follow',
        ),
        migrations.RemoveField(
            model_name='twitteraccount',
            name='hub',
        ),
        migrations.RemoveField(
            model_name='twitteraccount',
            name='name',
        ),
    ]
