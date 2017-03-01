# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-02-28 14:38
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields.hstore
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LoggerHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('project', django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True)),
                ('category', django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True)),
                ('user_id', django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True)),
                ('usergroup', django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True)),
                ('subset', django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True)),
                ('location', django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True)),
                ('observation', django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True)),
                ('comment', django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True)),
                ('action', django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True)),
                ('geometry', django.contrib.gis.db.models.fields.GeometryField(geography=True, null=True, srid=4326)),
                ('action_id', models.CharField(choices=[(b'created', b'created'), (b'deleted', b'deleted'), (b'updated', b'updated')], default=b'created', max_length=20)),
                ('historical', django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True)),
            ],
        ),
    ]