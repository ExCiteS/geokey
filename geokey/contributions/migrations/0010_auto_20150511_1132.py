# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.db import migrations


def clean_list(val):
    if val is not None and isinstance(val, str):
        return json.loads(val)

    return val


def clean_int(val):
    if val is not None and isinstance(val, str):
        return int(val)

    return val


def clean_number(val):
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


def clean_values(apps, schema_editor):
    Observation = apps.get_model("contributions", "Observation")
    for observation in Observation.objects.all():
        for field in observation.category.fields.all():
            if field.__class__.__name__ == 'NumericField':
                observation.properties[field.key] = clean_number(
                    observation.properties[field.key])
            if field.__class__.__name__ == 'LookupField':
                observation.properties[field.key] = clean_int(
                    observation.properties[field.key])
            if field.__class__.__name__ == 'MultipleLookupField':
                observation.properties[field.key] = clean_list(
                    observation.properties[field.key])

        observation.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0009_auto_20150420_1549'),
    ]

    operations = [
        migrations.RunPython(clean_values),
    ]
