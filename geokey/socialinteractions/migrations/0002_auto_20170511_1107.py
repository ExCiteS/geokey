# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('socialaccount', '0003_extra_data_default_dict'),
        ('projects', '0008_historicalproject'),
        ('socialinteractions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialInteractionPull',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('text_to_pull', models.TextField(null=True, blank=True)),
                ('frequency', models.CharField(default=b'daily', max_length=20, choices=[(b'weekly', b'weekly'), (b'monthly', b'monthly'), (b'daily', b'daily'), (b'forthnightly', b'forthnightly'), (b'hourly', b'hourly')])),
                ('status', models.CharField(default=b'active', max_length=20, choices=[(b'active', b'active'), (b'hold', b'hold')])),
                ('since_id', models.TextField(null=True, blank=True)),
                ('updated_at', models.DateTimeField(null=True)),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(related_name='socialinteractions_pull', to='projects.Project')),
                ('socialaccount', models.ForeignKey(related_name='socialinteractions_pull', to='socialaccount.SocialAccount')),
            ],
        ),
        migrations.AddField(
            model_name='socialinteraction',
            name='status',
            field=models.CharField(default=b'active', max_length=20, choices=[(b'active', b'active'), (b'hold', b'hold')]),
        ),
    ]
