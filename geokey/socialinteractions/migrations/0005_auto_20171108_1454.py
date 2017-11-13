# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialinteractions', '0004_auto_20171101_1538'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialinteraction',
            name='text_to_post',
            field=models.TextField(default=b'New contribution added to #$project$. Check it out here $link$', null=True, blank=True),
        ),
    ]
