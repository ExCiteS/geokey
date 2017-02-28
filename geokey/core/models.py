"""Models for logger."""

from django.db import models
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.gis.db import models as gis
from geokey.categories.models import Field
from django.contrib.postgres.fields import HStoreField
from geokey.core.signals import get_request


from .base import list_of_models, STATUS_ACTION, actions_dic


class LoggerHistory(models.Model):
    """Stores the loggers for each even created."""

    timestamp = models.DateTimeField(auto_now_add=True)
    project = HStoreField(null=True, blank=True)
    category = HStoreField(null=True, blank=True)
    user = HStoreField(null=True, blank=True)
    usergroup = HStoreField(null=True, blank=True)
    subset = HStoreField(null=True, blank=True)
    field = HStoreField(null=True, blank=True)
    observation = HStoreField(null=True, blank=True)
    comment = HStoreField(null=True, blank=True)
    action = HStoreField(null=True, blank=True)
    geometry = gis.GeometryField(geography=True, null=True)
    action_id = models.CharField(
        choices=STATUS_ACTION,
        default=STATUS_ACTION.created,
        max_length=20
    )
    historical = HStoreField(null=True, blank=True)



def create_new_log(sender, instance, actions_info, request):
    if actions_info:
        for action in actions_info:
            historical = {'class': sender.__name__}
            if action['id'] != 'updated':
                try:
                    historical['id'] = str(instance.history.latest('pk').pk)
                except:
                    historical['id'] = None
            else:
                historical = {}
            if hasattr(request, 'user'):
                user_info = {
                    'id': str(request.user.id),
                    'display_name': str(request.user)
                }
            else:
                user_info = {}
            log = LoggerHistory(
                action=action,
                user=user_info,
                historical=historical
            )
            if sender.__name__ == 'Project':
                log.project = {
                    'id': str(instance.id),
                    'name': instance.name
                }
            elif sender.__name__ == 'Comment':
                log.category = {
                    'id': str(instance.commentto.category.id),
                    'name': instance.commentto.category.name
                }
                log.project = {
                    'id': str(instance.commentto.category.project.id),
                    'name': instance.commentto.category.project.name
                }
                log.comment = {
                    'id': str(instance.id)}
                pass
            elif sender.__name__ == 'Observation':
                log.project = {
                    'id': str(instance.project.id),
                    'name': instance.project.name
                }
                log.category = {
                    'id': str(instance.category.id),
                    'name': instance.category.name
                }
                log.observation = {'id': str(instance.id)}
                log.geometry = instance.location.geometry
            elif sender.__name__ == 'UserGroup':
                log.project = {
                    'id': str(instance.project.id),
                    'name': instance.project.name
                }
                log.usergroup = {
                    'id': str(instance.id),
                    'name': instance.name
                }
            elif sender.__name__ == 'Category':
                log.category = {
                    'id': str(instance.id),
                    'name': instance.name
                }
                log.project = {
                    'id': str(instance.project.id),
                    'name': instance.project.name
                }
            elif sender.__name__ == 'Subset':
                log.subset = {
                    'id': str(instance.id),
                    'name': instance.name
                }
                log.project = {
                    'id': str(instance.project.id),
                    'name': instance.project.name
                }
            elif 'Field' in sender.__name__:
                field = Field.objects.latest('pk')
                log.category = {
                    'id': str(field.category.id),
                    'name': field.category.name
                }
                log.field = {
                    'id': str(field.id),
                    'name': field.name
                }
                log.project = {
                    'id': str(field.category.project.id),
                    'name': field.category.project.name
                }
            log.save()


def cross_check_fields(instance, obj):
    """

    Cross check if changes in there are changes in the instance.

    Parameters
    -----------
    instance: django model
        geokey object triggered by django.model.signals

    obj: object

    Returns
    --------
    actions: list str
        list of string with the text to be added on actions field on
        HistoryLogger.
    """
    actions_info = []
    class_name = instance.__class__.__name__

    for field, value in actions_dic[class_name].iteritems():
        if not instance.__dict__.get(field) == obj.__dict__.get(field):
            try:
                if (class_name == 'Project' and
                        instance.__dict__.get(field) == 'deleted'):
                    action_dic = {
                        'id': STATUS_ACTION.deleted,
                        'field': field,
                        'value': instance.__dict__.get(field)
                    }
                else:
                    action_dic = {
                        'id': value,
                        'field': field,
                        'value': instance.__dict__.get(field)
                    }
                actions_info.append(action_dic)
            except:
                pass
    return actions_info


"""
Receiver for pre_save and get updates.
"""


@receiver(pre_save)
def log_updates(sender, instance, *args, **kwargs):
    """Create logs when something updated in a model."""
    request = get_request()
    if sender.__name__ in list_of_models:
        try:
            obj = sender.objects.get(pk=instance.pk)
            create_new_log(
                sender,
                instance,
                cross_check_fields(instance, obj),
                request
            )
        except:
            pass

"""
Receiver for post_save and get creations.
"""


@receiver(post_save)
def log_created(sender, instance, created, **kwargs):
    """Create logs when something new is created in a model."""
    request = get_request()
    if sender.__name__ in list_of_models:
        if created:
            actions_info = {}
            actions_info['id'] = STATUS_ACTION.created
            create_new_log(
                sender,
                instance,
                [actions_info],
                request
            )
        else:
            try:
                log = LoggerHistory.objects.last()
                log.historical = {
                    'class': sender.__name__,
                    'id': str(instance.history.latest('pk').pk)
                }
                log.save()
            except:
                pass


"""
Receiver for post_deletes for UserGroup, Field, Subset and User
"""


@receiver(post_delete)
def log_delete(sender, instance, *args, **kwargs):
    """Create logs when something is deleted in a model."""
    request = get_request()
    try:
        instance.__class__.objects.get(pk=instance.id)
    except:
        if sender.__name__ == 'Field':
            actions_info = {'id': STATUS_ACTION.deleted}
            create_new_log(
                sender,
                instance,
                [actions_info],
                request
            )
        if sender.__name__ == 'UserGroup':
            actions_info = {'id': STATUS_ACTION.deleted}
            create_new_log(
                sender,
                instance,
                [actions_info],
                request
            )
        if sender.__name__ == 'Subset':
            actions_info = {'id': STATUS_ACTION.deleted}
            create_new_log(
                sender,
                instance,
                [actions_info],
                request
            )
