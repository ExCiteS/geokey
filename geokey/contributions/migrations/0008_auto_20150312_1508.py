# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0007_auto_20150312_1249'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalobservation',
            name='attributes',
        ),
        migrations.RemoveField(
            model_name='observation',
            name='attributes',
        ),
    ]
