# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def fix_twitteraccount_ptr(apps, schema_editor):
    Account = apps.get_model('posts', 'Account')
    TwitterAccount = apps.get_model('tweets', 'TwitterAccount')

    if TwitterAccount.objects.all().count() > 1:
        raise NotImplementd()

    tw = TwitterAccount.objects.update(account_ptr=Account.objects.first())


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0039_account_inheritance'),
        ('tweets', '0005_account_inheritance_alter_tweetaccount'),
    ]

    operations = [
        migrations.RunPython(fix_twitteraccount_ptr),
    ]
