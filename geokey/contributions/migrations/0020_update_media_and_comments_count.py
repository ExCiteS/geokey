# -*- coding: utf-8 -*-

from django.db import migrations, transaction, IntegrityError


def update_media_and_comments_count(apps, schema_editor):
    Observation = apps.get_model('contributions', 'Observation')

    for observation in Observation.objects.all():
        try:
            with transaction.atomic():
                observation.num_media = observation.files_attached.count()
                observation.num_comments = observation.comments.count()
                observation.save()
        except IntegrityError:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0019_auto_20181020_1915'),
    ]

    operations = [
        migrations.RunPython(update_media_and_comments_count)
    ]
