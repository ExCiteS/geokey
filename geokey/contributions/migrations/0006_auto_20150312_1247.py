# -*- coding: utf-8 -*-


from django.db import migrations
try:
    from django.contrib.postgres.fields import JSONField
except ImportError:
    from django_pgjson.fields import JsonBField as JSONField


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0005_auto_20150202_1135'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalobservation',
            name='properties',
            field=JSONField(default={}),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='observation',
            name='properties',
            field=JSONField(default={}),
            preserve_default=True,
        ),
    ]
