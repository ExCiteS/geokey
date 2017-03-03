"""Core models."""

from django.db.models.signals import (
    pre_save,
    post_save,
    post_delete,
    m2m_changed,
)
from django.dispatch import receiver
from django.contrib.postgres.fields import HStoreField

from model_utils.models import TimeStampedModel

from geokey.core.signals import get_request

from .base import STATUS_ACTION, LOG_MODELS, LOG_M2M_RELATIONS


class LoggerHistory(TimeStampedModel):
    """Store the event logs."""

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


def get_history(sender, instance):
    """Get the latest history entry of an instance."""
    try:
        print str(instance.history.latest('pk').pk),
        print sender.history.model.__name__
        history = {
            'id': str(instance.history.latest('pk').pk),
            'class': sender.history.model.__name__,
        }
    # TODO: Except when history model object does not exist
    except:
        history = None

    return history


def add_user_info(action, instance):
    """Add the user info to the action."""
    action_class = action.get('class')
    if action_class in ['Admins', 'UserGroup_users']:
        if hasattr(instance, 'user'):
            instance = instance.user
        action['user_id'] = str(instance.id)
        action['user_display_name'] = str(instance)

    return action


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
    elif hasattr(instance, 'project'):
        fields['project'] = instance.project

    if class_name == 'Category':
        fields['category'] = instance
    elif hasattr(instance, 'category'):
        fields['category'] = instance.category

    if 'UserGroup' in class_name:
        fields['usergroup'] = instance
    elif class_name == 'Field':
        fields['project'] = instance.category.project
        fields['field'] = instance
    elif class_name == 'Location':
        fields['location'] = instance
    elif class_name == 'Observation':
        fields['location'] = instance.location
        fields['observation'] = instance
    elif class_name == 'Comment':
        fields['project'] = instance.commentto.project
        fields['category'] = instance.commentto.category
        fields['location'] = instance.commentto.location
        fields['observation'] = instance.commentto
        fields['comment'] = instance
    elif class_name == 'Subset':
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
    action_id = STATUS_ACTION.updated
    class_name = get_class_name(new_instance)

    changed_fields = []
    usergroup_permission_fields = {}

    for field in LOG_MODELS.get(new_instance.__class__.__name__, {}):
        new_value = new_instance.__dict__.get(field)
        original_value = original_instance.__dict__.get(field)
        if new_value != original_value:
            if field in ['can_contribute', 'can_moderate']:
                usergroup_permission_fields[field] = new_value
            else:
                # Action "deleted" - nothing gets deleted, only status change
                if field == 'status' and new_value == 'deleted':
                    action_id = STATUS_ACTION.deleted

                changed_field = {
                    'id': action_id,
                    'class': class_name,
                    'field': field,
                }

                if field not in ['name', 'geographic_extent', 'properties']:
                    changed_field['value'] = str(new_value)

                changed_fields.append(changed_field)

    if len(usergroup_permission_fields):
        changed_field = {
            'id': action_id,
            'class': class_name,
            'field': 'can_contribute',
            'value': str(True),
        }

        if usergroup_permission_fields.get('can_moderate') is True:
            changed_field['field'] = 'can_moderate'
        elif usergroup_permission_fields.get('can_contribute') is False:
            changed_field['field'] = 'can_view'

        changed_fields.append(changed_field)

    return changed_fields


@receiver(pre_save)
def logs_on_pre_save(sender, instance, **kwargs):
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
def log_on_post_save(sender, instance, created, **kwargs):
    """Finalise initiated logs or create a new one when instance is created."""
    if sender.__name__ in LOG_MODELS:
        logs = []

        if created:
            action = add_user_info({
                'id': STATUS_ACTION.created,
                'class': get_class_name(sender)
            }, instance)
            logs.append(generate_log(sender, instance, action))
        elif hasattr(instance, '_logs') and instance._logs is not None:
            logs = instance._logs

        for log in logs:
            log.historical = get_history(sender, instance)
            log.save()


@receiver(post_delete)
def log_on_post_delete(sender, instance, **kwargs):
    """Create a log when instance is deleted."""
    if sender.__name__ in LOG_MODELS:
        action = add_user_info({
            'id': STATUS_ACTION.deleted,
            'class': get_class_name(sender),
        }, instance)

        log = generate_log(sender, instance, action)
        log.historical = get_history(sender, instance)
        log.save()


@receiver(m2m_changed)
def log_on_m2m_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
    """Create a log when object is added to or removed from M2M relation."""
    if sender.__name__ in LOG_M2M_RELATIONS and 'post_' in action:
        for pk in pk_set:
            action = add_user_info({
                'id': STATUS_ACTION.updated,
                'class': sender.__name__,
                'subaction': action.replace('post_', ''),
            }, model.objects.get(pk=pk))

            log = generate_log(sender, instance, action)
            log.save()
