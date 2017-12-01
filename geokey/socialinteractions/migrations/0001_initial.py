# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('socialaccount', '0003_extra_data_default_dict'),
        ('projects', '0008_historicalproject'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialInteractionPost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('text_to_post', models.TextField(null=True, blank=True)),
                ('link', models.TextField(null=True, blank=True)),
                ('status', models.CharField(default=b'active', max_length=20, choices=[(b'active', b'active'), (b'inactive', b'inactive')])),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(related_name='socialinteractions_post', to='projects.Project')),
                ('socialaccount', models.ForeignKey(related_name='socialinteractions_post', to='socialaccount.SocialAccount')),
            ],
        ),
        migrations.CreateModel(
            name='SocialInteractionPull',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('text_to_pull', models.TextField(null=True, blank=True)),
                ('frequency', models.CharField(default=b'daily', max_length=20, choices=[(b'5min', b'5min'), (b'10min', b'10min'), (b'20min', b'20min'), (b'30min', b'30min'), (b'hourly', b'hourly'), (b'daily', b'daily'), (b'weekly', b'weekly'), (b'fortnightly', b'fortnightly'), (b'monthly', b'monthly')])),
                ('status', models.CharField(default=b'active', max_length=20, choices=[(b'active', b'active'), (b'inactive', b'inactive')])),
                ('since_id', models.TextField(null=True, blank=True)),
                ('updated_at', models.DateTimeField(null=True)),
                ('checked_at', models.DateTimeField(null=True)),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(related_name='socialinteractions_pull', to='projects.Project')),
                ('socialaccount', models.ForeignKey(related_name='socialinteractions_pull', to='socialaccount.SocialAccount')),
            ],
        ),
    ]
