# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.db import migrations


def copy_filters(apps, schema_editor):
    Rule = apps.get_model("datagroupings", "Rule")
    for rule in Rule.objects.all():
        constraints = {}
        if rule.filters is not None:
            for key in rule.filters:
                try:
                    constraints[key] = json.loads(rule.filters[key])
                except ValueError:
                    constraints[key] = rule.filters[key]

            rule.constraints = constraints
            rule.save()


class Migration(migrations.Migration):

    dependencies = [
        ('datagroupings', '0004_rule_contraints'),
    ]

    operations = [
        migrations.RunPython(copy_filters),
    ]
