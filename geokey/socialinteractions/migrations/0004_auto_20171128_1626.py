# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialinteractions', '0003_auto_20171024_1400'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialinteraction',
            name='link',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='socialinteractionpull',
            name='checked_at',
            field=models.DateTimeField(null=True),
        ),
    ]
