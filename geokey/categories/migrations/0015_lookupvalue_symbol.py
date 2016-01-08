# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0014_auto_20160104_1409'),
    ]

    operations = [
        migrations.AddField(
            model_name='lookupvalue',
            name='symbol',
            field=models.ImageField(max_length=500, null=True, upload_to=b'symbols'),
        ),
    ]
