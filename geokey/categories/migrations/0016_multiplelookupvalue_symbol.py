# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0015_lookupvalue_symbol'),
    ]

    operations = [
        migrations.AddField(
            model_name='multiplelookupvalue',
            name='symbol',
            field=models.ImageField(max_length=500, null=True, upload_to=b'symbols'),
        ),
    ]
