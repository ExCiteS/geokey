# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0018_historicalcategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='transparency',
            field=models.IntegerField(default=100),
        ),
        migrations.AddField(
            model_name='historicalcategory',
            name='transparency',
            field=models.IntegerField(default=100),
        ),
    ]
