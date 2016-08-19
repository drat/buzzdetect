# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def set_post_account(apps, schema_editor):
    Account = apps.get_model('posts', 'Account')
    Post = apps.get_model('posts', 'Post')

    account = Account.objects.first()
    if account:
        Post.objects.all().update(account=account)

class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0039_account_inheritance'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='account',
            field=models.ForeignKey(null=True, to='posts.Account'),
            preserve_default=False,
        ),
        migrations.RunPython(set_post_account),
        migrations.AlterField(
            model_name='post',
            name='account',
            field=models.ForeignKey(null=False, to='posts.Account'),
            preserve_default=False,
        ),
    ]
