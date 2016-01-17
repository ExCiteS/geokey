# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0013_auto_20150130_1440'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='symbol',
            field=models.ImageField(max_length=500, null=True, upload_to=b'symbols'),
        ),
    ]
