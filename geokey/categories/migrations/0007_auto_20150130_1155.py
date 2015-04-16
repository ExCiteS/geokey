# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def update_display_field(apps, schema_editor):
    Category = apps.get_model("categories", "Category")
    Field = apps.get_model("categories", "Field")
    for category in Category.objects.all():
        try:
            first_field = category.fields.get(order=0)
            category.display_field = first_field
            category.save()
        except Field.DoesNotExist:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0006_category_display_field'),
    ]

    operations = [
        migrations.RunPython(update_display_field),
    ]
