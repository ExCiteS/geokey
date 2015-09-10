# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0013_auto_20150130_1440'),
        ('projects', '0005_auto_20150202_1041'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contributions', '0012_auto_20150807_0854'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalobservation',
            name='category_id',
        ),
        migrations.RemoveField(
            model_name='historicalobservation',
            name='creator_id',
        ),
        migrations.RemoveField(
            model_name='historicalobservation',
            name='location_id',
        ),
        migrations.RemoveField(
            model_name='historicalobservation',
            name='project_id',
        ),
        migrations.RemoveField(
            model_name='historicalobservation',
            name='updator_id',
        ),
        migrations.AddField(
            model_name='historicalobservation',
            name='category',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='categories.Category', null=True),
        ),
        migrations.AddField(
            model_name='historicalobservation',
            name='creator',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicalobservation',
            name='location',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='contributions.Location', null=True),
        ),
        migrations.AddField(
            model_name='historicalobservation',
            name='project',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='projects.Project', null=True),
        ),
        migrations.AddField(
            model_name='historicalobservation',
            name='search_index',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalobservation',
            name='updator',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='observation',
            name='search_index',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalobservation',
            name='history_user',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='historicalobservation',
            name='search_matches',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='observation',
            name='search_matches',
            field=models.TextField(null=True, blank=True),
        ),
    ]
