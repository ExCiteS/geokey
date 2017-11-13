# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialinteractions', '0005_auto_20171108_1454'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialinteractionpull',
            name='checked_at',
            field=models.DateTimeField(null=True),
        ),
    ]
