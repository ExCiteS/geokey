"""Models for logger."""

from django.db import models
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.gis.db import models as gis

from .base import actions_dic, list_of_models, STATUS_ACTION


class LoggerHistory(models.Model):
    """Stores the loggers for each even created """

    timestamp = models.DateTimeField(auto_now_add=True)
    project_id = models.CharField(null=True, max_length=1000)
    category_id = models.CharField(null=True, max_length=1000)
    user_id = models.CharField(null=True,max_length=1000)
    action  = models.CharField(max_length=300)
    geometry = gis.GeometryField(geography=True, null=True)
    action_id = models.CharField(
        choices=STATUS_ACTION,
        default=STATUS_ACTION.created,
        max_length=20
    )


def create_log(sender, instance, actions):

    """ Create a log on LoggerHistory depending the sender.

    Parameters
    -----------
    sender : django.db.models.base.ModeBase class
        sender provided by the django.model.signals.
    instance : django model
        geokey model triggered by django.model.signals
    actions : list of str
        list of strings which contains the actions will be added to the action
        field on HistoryLogger table

    """
    if actions:
        for action in actions:
            if 'created' in action:
                action_id = STATUS_ACTION.created
            elif 'deleted' in action:
                action_id = STATUS_ACTION.deleted
            else:
                action_id = STATUS_ACTION.updated
            log = LoggerHistory(
                action=action,
                action_id=action_id
            )

            if sender.__name__ == 'User':
                log.user_id = instance.id
            if sender.__name__ == 'Project':
                log.project_id = instance.id
                log.user_id = instance.creator.id
            if sender.__name__ == 'Comment':
                log.project_id = instance.commentto.category.project.id
                log.user_id = instance.creator.id
                log.category_id = instance.commentto.category.id
                pass
            if sender.__name__ == 'Observation':
                log.project_id = instance.category.id
                log.project_id = instance.project.id
                log.user_id = instance.creator.id
                log.geometry = instance.location.geometry
            if sender.__name__ == 'UserGroup':
                log.project_id = instance.project.id
                #log.user_id = instance.creator.id
            if sender.__name__ == 'Category':
                log.category_id = instance.id
                log.project_id = instance.project.id
                log.user_id = instance.creator.id
            if sender.__name__ == 'Subset':
                log.category_id = instance.id
                log.project_id = instance.project.id
                log.user_id = instance.creator.id
            log.save()
    # return log


def checkIsPrivate(isprivate):
    """
    Checks if Project is privite and provides string with the text to be added
    to action field in log.

    Parameters
    -----------
    isprivate = str
        status field value in Project object.

    Returns
    --------
    status = str
        text to be added on action field Historylogger.
    """

    status = 'public'
    if isprivate == True:
        status = 'private'
    return status

def cross_check_fields(instance,obj):
    """
    Cross check the fiels of the instance passed and check if there have been 
    changes.

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
    actions = []
    class_name = instance.__class__.__name__
    for field, value in actions_dic[class_name].iteritems():
        if not instance.__dict__.get(field) == obj.__dict__.get(field):
            try:
                action = value                
                if field == 'isprivate' and class_name == 'Project':
                    action = action + checkIsPrivate(field)
                if field == 'status' and class_name == 'Observation':
                    action = action + instance.__dict__.get(field)
                if field == 'status' and class_name == 'Category':
                    action = action + instance.__dict__.get(field)
                if field == 'status' and 'Field' in class_name:
                    action = action + instance.__dict__.get(field)
                actions.append(action)
            except:
                pass
    return actions

"""
Receiver for pre_save and get updates.
""" 
@receiver(pre_save)
def log_updates(sender, instance, *args,  **kwargs):
    if sender.__name__ in list_of_models:
        try:
            obj = sender.objects.get(pk=instance.pk)
            create_log(sender, instance, cross_check_fields(instance, obj))
        except:
            pass

"""
Receiver for post_save and get creations.
""" 
@receiver(post_save)
def log_created(sender, instance, created, **kwargs):
    if sender.__name__ in list_of_models:
        if created:
            create_log(sender, instance, [sender.__name__+" created"])


"""
Receiver for post_deletes for UserGroup, Field and Subset
""" 
@receiver(post_delete) 
def log_delete(sender, instance, *args,  **kwargs):
    try:
        instance.__class__.objects.get(pk=instance.id)
    except:
        if sender.__name__ == 'Field':
            try:
                project_id = instance.category.project.id
            except:
                project_id = 0
            action = "Field deleted"
            LoggerHistory.objects.create(
                project_id=project_id,
                action=action,
                action_id=STATUS_ACTION.deleted
            )
        if sender.__name__  == 'UserGroup':
            project_id = instance.project.id
            action = sender.__name__ +" deleted"
            LoggerHistory.objects.create(
                project_id=project_id,
                action=action,
                action_id=STATUS_ACTION.deleted
            )
        if sender.__name__  == 'Subset':
            project_id = instance.project.id
            action = sender.__name__ +" deleted"
            LoggerHistory.objects.create(
                project_id=project_id,
                action=action,
                user_id = instance.creator.id,
                action_id=STATUS_ACTION.deleted
            )
        if sender.__name__  == 'User':
            action = sender.__name__ +" deleted"
            LoggerHistory.objects.create(
                user_id=instance.id,
                action=action,
                action_id=STATUS_ACTION.deleted
            )
