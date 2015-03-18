# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def populate_display_field(apps, schema_editor):
    Observation = apps.get_model("contributions", "Observation")
    for observation in Observation.objects.all():
        first_field = observation.category.fields.get(order=0)
        value = observation.attributes.get(first_field.key)
        observation.display_field = '%s:%s' % (first_field.key, value)
        observation.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0003_auto_20150121_1544'),
    ]

    operations = [
        migrations.RunPython(populate_display_field),
    ]
