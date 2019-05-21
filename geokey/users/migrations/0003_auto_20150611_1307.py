# -*- coding: utf-8 -*-


from django.db import models, migrations
try:
    from django.contrib.postgres.fields import JSONField
except ImportError:
    from django_pgjson.fields import JsonBField as JSONField


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20150106_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='usergroup',
            name='filters',
            field=JSONField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='usergroup',
            name='where_clause',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
