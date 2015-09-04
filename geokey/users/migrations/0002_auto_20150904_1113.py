# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_squashed_0004_auto_20150617_0902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='display_name',
            field=models.CharField(unique=True, max_length=50, error_messages={b'unique': b'A user is already registered with this display name.'}),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(unique=True, max_length=75, error_messages={b'unique': b'A user is already registered with this email address.'}),
            preserve_default=True,
        ),
    ]
