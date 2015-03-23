# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0005_auto_20150112_1731'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='display_field',
            field=models.ForeignKey(related_name='display_field_of', default=None, to='categories.Field', null=True),
            preserve_default=False,
        ),
    ]
