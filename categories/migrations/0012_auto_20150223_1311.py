# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0011_auto_20150220_1413'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['order']},
        ),
        migrations.AddField(
            model_name='category',
            name='order',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
