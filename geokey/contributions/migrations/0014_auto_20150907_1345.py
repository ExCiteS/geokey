# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import re


def create_search_index(apps, schema_editor):
    Observation = apps.get_model('contributions', 'Observation')

    for o in Observation.objects.all():
        search_index = []

        fields = o.search_matches.split('#####')
        for field in fields:
            if field:
                value = field.split(':')[1]

                cleaned = re.sub(r'[\W_]+', ' ', value)
                terms = cleaned.lower().split()

                search_index = search_index + list(
                    set(terms) - set(search_index)
                )

        o.search_index = ','.join(search_index)
        o.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0013_auto_20150907_1345'),
    ]

    operations = [
        migrations.RunPython(create_search_index)
    ]
