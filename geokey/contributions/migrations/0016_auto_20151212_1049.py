# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0015_auto_20150907_1345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='observation',
            name='location',
            field=models.ForeignKey(related_name='locations', to='contributions.Location', null=True),
        ),
    ]
