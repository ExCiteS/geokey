# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from geokey.contributions.models import Observation


def populate_display_field(apps, schema_editor):
    Category = apps.get_model("categories", "Category")
    # Observation = apps.get_model("contributions", "Observation")

    for category in Category.objects.all():
        if category.display_field is not None:
            for obs in Observation.objects.filter(category=category):
                obs.update_display_field()
                obs.save()


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0012_auto_20150223_1311'),
    ]

    operations = [
        migrations.RunPython(populate_display_field),
    ]
