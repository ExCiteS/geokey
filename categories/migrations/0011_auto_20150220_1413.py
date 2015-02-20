# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0010_auto_20150202_1023'),
    ]

    operations = [
        migrations.AddField(
            model_name='textfield',
            name='maxlength',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='textfield',
            name='textarea',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
