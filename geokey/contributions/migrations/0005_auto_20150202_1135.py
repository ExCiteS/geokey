# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def update_search_matches(apps, schema_editor):
    Observation = apps.get_model("contributions", "Observation")
    for observation in Observation.objects.all():
        observation.update_search_matches()
        observation.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0004_auto_20150121_1455'),
    ]

    operations = [
        migrations.RunPython(update_search_matches),
    ]
