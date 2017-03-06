# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_pgjson.fields
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0008_historicalproject'),
        ('users', '0007_auto_20151006_1110'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalUserGroup',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(null=True, blank=True)),
                ('can_contribute', models.BooleanField(default=True)),
                ('can_moderate', models.BooleanField(default=False)),
                ('filters', django_pgjson.fields.JsonBField(null=True, blank=True)),
                ('where_clause', models.TextField(null=True, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('project', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='projects.Project', null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical user group',
            },
        ),
    ]
