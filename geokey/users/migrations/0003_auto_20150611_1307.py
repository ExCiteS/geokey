# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_pgjson.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20150106_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='usergroup',
            name='filters',
            field=django_pgjson.fields.JsonBField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='usergroup',
            name='where_clause',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
