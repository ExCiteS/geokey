# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='display_name',
            field=models.CharField(unique=True, max_length=50, error_messages={b'unique': b'A user is already registered with this display name.'}),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(unique=True, max_length=75, error_messages={b'unique': b'A user is already registered with this email address.'}),
            preserve_default=True,
        ),
    ]
