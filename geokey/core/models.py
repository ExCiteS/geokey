"""Core models."""

from django.db import models
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.contrib.postgres.fields import HStoreField

from geokey.core.signals import get_request

from .base import STATUS_ACTION, LOG_MODELS


class LoggerHistory(models.Model):
    """Store the event logs."""

    timestamp = models.DateTimeField(auto_now_add=True)
    user = HStoreField(null=True, blank=True)
    project = HStoreField(null=True, blank=True)
    usergroup = HStoreField(null=True, blank=True)
    category = HStoreField(null=True, blank=True)
    field = HStoreField(null=True, blank=True)
    location = HStoreField(null=True, blank=True)
    observation = HStoreField(null=True, blank=True)
    comment = HStoreField(null=True, blank=True)
    subset = HStoreField(null=True, blank=True)
    action = HStoreField(null=True, blank=True)
    historical = HStoreField(null=True, blank=True)


def get_class_name(instance_class):
    """Get the instance class name."""
    if not hasattr(instance_class, '__bases__'):
        instance_class = instance_class.__class__

    bases = [x.__name__ for x in instance_class.__bases__]
    if 'Field' in bases:
        return 'Field'

    return instance_class.__name__


def generate_log(sender, instance, action):
    """Generate a single log (without saving to DB)."""
    log = LoggerHistory(action=action)

    request = get_request()
    if hasattr(request, 'user'):
        log.user = {
            'id': str(request.user.id),
            'display_name': str(request.user),
        }

    fields = {}
    class_name = get_class_name(sender)

    if class_name == 'Project':
        fields['project'] = instance
    elif class_name == 'UserGroup':
        fields['project'] = instance.project
        fields['usergroup'] = instance
    elif class_name == 'Category':
        fields['project'] = instance.project
        fields['category'] = instance
    elif class_name == 'Field':
        fields['project'] = instance.category.project
        fields['category'] = instance.category
        fields['field'] = instance
    elif class_name == 'Location':
        fields['location'] = instance
    elif class_name == 'Observation':
        fields['project'] = instance.project
        fields['category'] = instance.category
        fields['location'] = instance.location
        fields['observation'] = instance
    elif class_name == 'Field':
        fields['project'] = instance.category.project
        fields['category'] = instance.category
        fields['field'] = instance
    elif class_name == 'Subset':
        fields['project'] = instance.project
        fields['subset'] = instance

    for field, instance in fields.iteritems():
        value = {'id': str(instance.id)}

        # Not all models have names
        if hasattr(instance, 'name'):
            value['name'] = instance.name

        # Fields for categories should also have type
        if field == 'field':
            value['type'] = sender.__name__

        setattr(log, field, value)

    return log


def cross_check_fields(new_instance, original_instance):
    """Check for changed fields between new and original instances."""
    changed_fields = []

    for field in LOG_MODELS.get(new_instance.__class__.__name__, {}):
        new_value = new_instance.__dict__.get(field)
        original_value = original_instance.__dict__.get(field)
        if new_value != original_value:
            action_id = STATUS_ACTION.updated

            # Action is "deleted" - nothing gets deleted, only status change
            if field == 'status' and new_value == 'deleted':
                action_id = STATUS_ACTION.deleted

            changed_field = {
                'id': action_id,
                'class': get_class_name(new_instance),
                'field': field,
            }

            if field not in ['name', 'geographic_extent', 'properties']:
                changed_field['value'] = str(new_value)

            changed_fields.append(changed_field)

    return changed_fields


@receiver(pre_save)
def logs_on_pre_save(sender, instance, *args, **kwargs):
    """Initiate logs when instance get updated."""
    if sender.__name__ in LOG_MODELS:
        logs = []

        try:
            original_instance = sender.objects.get(pk=instance.pk)
            for field in cross_check_fields(instance, original_instance):
                logs.append(generate_log(sender, instance, field))
        except sender.DoesNotExist:
            pass

        instance._logs = logs


@receiver(post_save)
def log_on_post_save(sender, instance, created, *args, **kwargs):
    """Finalise initiated logs or create a new one when instance is created."""
    if sender.__name__ in LOG_MODELS:
        logs = []

        if created:
            logs.append(generate_log(
                sender,
                instance,
                {
                    'id': STATUS_ACTION.created,
                    'class': get_class_name(sender),
                }))
        elif hasattr(instance, '_logs') and instance._logs is not None:
            logs = instance._logs

        try:
            historical = {
                'id': str(instance.history.latest('pk').pk),
                'class': sender.history.model.__name__,
            }
        # TODO: Except when history model object does not exist
        except:
            historical = None

        for log in logs:
            log.historical = historical
            log.save()


@receiver(post_delete)
def log_on_post_delete(sender, instance, *args, **kwargs):
    """Create a log when instance is deleted."""
    if sender.__name__ in LOG_MODELS:
        log = generate_log(
            sender,
            instance,
            {
                'id': STATUS_ACTION.deleted,
                'class': get_class_name(sender),
            })
        log.save()
