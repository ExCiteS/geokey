# -*- coding: utf-8 -*-


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20150611_1307'),
    ]

    operations = [
        migrations.RunSQL('DROP TABLE IF EXISTS users_groupingusergroup;')
    ]
