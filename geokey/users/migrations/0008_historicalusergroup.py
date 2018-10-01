# -*- coding: utf-8 -*-


from django.db import migrations, models
try:
    from django.contrib.postgres.fields import JSONField
except ImportError:
    from django_pgjson.fields import JsonBField as JSONField
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0008_historicalproject'),
        ('users', '0007_auto_20151006_1110'),
        ('users', '0004_auto_20150617_0902'),
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
                ('filters', JSONField(null=True, blank=True)),
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
