# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from contributions.models.contributions import Observation


def copy_attributes(apps, schema_editor):
    for observation in Observation.objects.all():
        properties = {}
        for field in observation.category.fields.all():
            value = observation.attributes.get(field.key)
            if value is not None:
                properties[field.key] = field.convert_from_string(value)

        observation.properties = properties
        observation.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0006_auto_20150312_1247'),
    ]

    operations = [
        migrations.RunPython(copy_attributes),
    ]
