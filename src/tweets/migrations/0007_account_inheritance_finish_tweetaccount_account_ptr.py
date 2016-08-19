# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0039_account_inheritance'),
        ('tweets', '0006_account_inheritance_link_accounts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='twitteraccount',
            name='account_ptr',
            field=models.OneToOneField(parent_link=True, primary_key=True, auto_created=True, null=False, serialize=False, to='posts.Account'),
            preserve_default=False,
        ),
    ]
