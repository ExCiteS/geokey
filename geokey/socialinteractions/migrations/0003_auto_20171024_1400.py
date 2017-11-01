# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialinteractions', '0002_auto_20170511_1107'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialinteraction',
            name='status',
            field=models.CharField(default=b'active', max_length=20, choices=[(b'active', b'active'), (b'inactive', b'inactive')]),
        ),
        migrations.AlterField(
            model_name='socialinteractionpull',
            name='frequency',
            field=models.CharField(default=b'daily', max_length=20, choices=[(b'5min', b'5min'), (b'10min', b'10min'), (b'20min', b'20min'), (b'30min', b'30min'), (b'weekly', b'weekly'), (b'monthly', b'monthly'), (b'daily', b'daily'), (b'forthnightly', b'forthnightly'), (b'hourly', b'hourly')]),
        ),
        migrations.AlterField(
            model_name='socialinteractionpull',
            name='status',
            field=models.CharField(default=b'active', max_length=20, choices=[(b'active', b'active'), (b'inactive', b'inactive')]),
        ),
    ]
