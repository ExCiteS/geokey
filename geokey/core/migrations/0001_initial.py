# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LoggerHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('user', django.contrib.postgres.fields.hstore.HStoreField(null=True, blank=True)),
                ('project', django.contrib.postgres.fields.hstore.HStoreField(null=True, blank=True)),
                ('usergroup', django.contrib.postgres.fields.hstore.HStoreField(null=True, blank=True)),
                ('category', django.contrib.postgres.fields.hstore.HStoreField(null=True, blank=True)),
                ('field', django.contrib.postgres.fields.hstore.HStoreField(null=True, blank=True)),
                ('location', django.contrib.postgres.fields.hstore.HStoreField(null=True, blank=True)),
                ('observation', django.contrib.postgres.fields.hstore.HStoreField(null=True, blank=True)),
                ('comment', django.contrib.postgres.fields.hstore.HStoreField(null=True, blank=True)),
                ('mediafile', django.contrib.postgres.fields.hstore.HStoreField(null=True, blank=True)),
                ('subset', django.contrib.postgres.fields.hstore.HStoreField(null=True, blank=True)),
                ('action', django.contrib.postgres.fields.hstore.HStoreField(null=True, blank=True)),
                ('historical', django.contrib.postgres.fields.hstore.HStoreField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
