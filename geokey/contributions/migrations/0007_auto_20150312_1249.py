# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def convert_value(val):
    if val is not None and isinstance(val, str):
        try:  # it's an int
            return int(val)
        except ValueError:
            pass

        try:  # it's a float
            return float(val)
        except ValueError:
            pass

    # cannot convert to number, returns string or None
    return val


def copy_attributes(apps, schema_editor):
    Observation = apps.get_model("contributions", "Observation")
    for observation in Observation.objects.all():
        properties = {}
        for field in observation.category.fields.all():
            value = observation.attributes.get(field.key)
            if value is not None:
                properties[field.key] = convert_value(value)

        observation.properties = properties
        observation.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0006_auto_20150312_1247'),
    ]

    operations = [
        migrations.RunPython(copy_attributes),
    ]
