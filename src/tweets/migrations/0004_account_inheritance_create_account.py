# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def create_account(apps, schema_editor):
    Account = apps.get_model('posts', 'Account')
    TwitterAccount = apps.get_model('tweets', 'TwitterAccount')

    if TwitterAccount.objects.all().count() > 1:
        raise NotImplementd()
    elif TwitterAccount.objects.all().count() == 0:
        return

    tw = TwitterAccount.objects.first()
    Account.objects.create(
        pk=tw.pk,
        name=tw.name,
        follow=tw.follow,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0039_account_inheritance'),
        ('tweets', '0003_add_hub'),
    ]

    operations = [
        migrations.RunPython(create_account),
    ]
