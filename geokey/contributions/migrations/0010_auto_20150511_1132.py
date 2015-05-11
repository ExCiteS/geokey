# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.db import migrations


def clean_list(val):
    if val is not None and (isinstance(val, str) or isinstance(val, unicode)):
        return json.loads(val)

    return val


def clean_int(val):
    if val is not None and (isinstance(val, str) or isinstance(val, unicode)):
        return int(val)

    return val


def clean_number(val):
    if val is not None and (isinstance(val, str) or isinstance(val, unicode)):
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
    NumericField = apps.get_model("categories", "NumericField")
    LookupField = apps.get_model("categories", "LookupField")
    MultipleLookupField = apps.get_model("categories", "MultipleLookupField")

    for field in NumericField.objects.all():
        for observation in Observation.objects.filter(category=field.category):
            if observation.properties:
                value = observation.properties.get(field.key)
                if value:
                    observation.properties[field.key] = clean_number(value)
                    observation.save()

    for field in LookupField.objects.all():
        for observation in Observation.objects.filter(category=field.category):
            if observation.properties:
                value = observation.properties.get(field.key)
                if value:
                    observation.properties[field.key] = clean_int(value)
                    observation.save()

    for field in MultipleLookupField.objects.all():
        for observation in Observation.objects.filter(category=field.category):
            if observation.properties:
                value = observation.properties.get(field.key)
                if value:
                    observation.properties[field.key] = clean_list(value)
                    observation.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0009_auto_20150420_1549'),
    ]

    operations = [
        migrations.RunPython(clean_values),
    ]
