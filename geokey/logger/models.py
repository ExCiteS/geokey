"""Models for logger."""

from django.db import models
from django.db.models.signals import post_save, pre_save, pre_delete, m2m_changed, post_delete
from django.dispatch import receiver
from django.contrib.gis.db import models as gis

from geokey.projects.models import Project
from geokey.categories.models import Category
from geokey.subsets.models import Subset
from geokey.users.models import UserGroup
from geokey.contributions.models import Comment

import datetime


class LoggerHistory(models.Model):
    """Stores the loggers for each even created """

    timestamp = models.DateTimeField(auto_now_add=True)
    project_id = models.CharField(null=True, max_length=1000)
    category_id = models.CharField(null=True, max_length=1000)
    user_id = models.CharField(null=True,max_length=1000)
    accion  = models.CharField(max_length=300)
    geometry = gis.GeometryField(geography=True, null=True)



#######
list_of_models = (
    'User',
    'Category',
    'Subset',
    'Project',
    'Observation',
    'Field',
    'Comment',
    'UserGroup',
    'TextField',
    'NumericField',
    'DateTimeField',
    'DateField',
    'TimeField',
    'LookupField',
    'MultipleLookupField',
    'Field'
)
#######

#######
accions_dic = {
    'User':
    {
        'display_name': 'User changed name'
    },

    'Comment':
    {
        'status': 'Comment removed',
        'review_status': 'Comment review status  to ',
    },
    'Observation':
    {
        # '_location_cache': 'Location has been changed',
        'status': 'Observation is '
    },
    'Field':
    {
        # '_location_cache': 'Location has been changed',
        'Required': 'Field is required'
    },
    'Subset':
    {
        'name': 'Subset renamed'
    },
    'TextField':
    {
        'name': 'Field renamed',
        'status': 'Field is '
    },
    'NumericField':
    {
        'name': 'Field renamed',
        'status': 'Field is '
    },
    'DateTimeField':
    {
        'name': 'Field renamed',
        'status': 'Field is '
    },
    'TimeField':
    {
        'name': 'Field renamed',
        'status': 'Field is '
    },
    'LookupField':
    {
        'name': 'Field renamed',
        'status': 'Field is '
    },
    'DateField':
    {
        'name': 'Field renamed',
        'status': 'Field is '
    },
    'MultipleLookupField':
    {
        'name': 'Field renamed',
        'status': 'Field is '
    },
    'UserGroup':
    {
        'name': 'User groups renamed',
        'can_moderate': 'User groups permissions changed'
    },
    'Category':
    {
        'name': 'Category renamed',
        'status': 'Category is ',
        'default_status': 'Category default status changed'
    },
    'Project':
    {
        'name': 'Project renamed',
        'geographic_extent' : 'Project geogr. ext. changed',
        'everyone_contributes': 'Project permissions changed',
        'isprivate': 'Project is ',
        'status': 'Project deleted'
    }
}

#######


def create_log(sender, instance, accions):

    """ Create a log on LoggerHistory depending the sender.

    Parameters
    -----------
    sender : django.db.models.base.ModeBase class
        sender provided by the django.model.signals.
    instance : django model
        geokey model triggered by django.model.signals
    accions : list of str
        list of strings which contains the accions will be added to the accion
        field on HistoryLogger table

    """
    if accions:
        print type(instance)
        for accion in accions:
            log = LoggerHistory(
            timestamp=datetime.datetime.now(),
            project_id=0,
            accion=accion
            )
            if sender.__name__ == 'User':
                log.user_id = instance.id
            if sender.__name__ == 'Project':
                log.project_id = instance.id
                log.user_id = instance.creator.id
            if sender.__name__ == 'Comment':
                log.project_id = instance.commentto.project.id
                log.user_id = instance.creator.id
                pass
            if sender.__name__ == 'Observation':
                log.project_id = instance.project.id
                log.user_id = instance.creator.id
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


def checkFieldStatus(status_value):
    """
    Checks Field status and provides string with the text to be added
    to accion field in the log.

    Parameters
    -----------
    status_value : str
        status field value in Field object.

    Returns
    --------
    status : str
        text to be added on accion field Historylogger. 

    """
    status = 'active'
    if status_value == 'inactive':
        status = 'inactive'
    if status_value == 'deleted':
        status = 'deleted'
    return status

def checkCategoryStatus(status_value):
    """
    Checks Category status and provides string with the text to be added
    to accion field in log.

    Parameters
    -----------
    status_value : str
        status field value in Category object.

    Returns
    --------
    status : str
        text to be added on accion field Historylogger.

    """

    status = 'active'
    if status_value == 'invactive':
        status = 'pending'
    if status_value == 'deleted':
        status = 'deleted'
    return status

def checkObservationStatus(status_value):
    """
    Checks observation status and provides string with the text to be added
    to accion field in log

    Parameters
    -----------
    status_value = str
        status field value in Observation object
    Returns
    --------
    status = str
        text to be added on accion field Historylogger 
    """

    status = 'active'
    if status_value == 'draft':
        status = 'draft'
    if status_value == 'review':
        status = 'review'
    if status_value == 'pending':
        status = 'pending'
    if status_value == 'deleted':
        status = 'deleted'
    return status

def checkIsPrivate(isprivate):
    """
    Checks if Project is privite and provides string with the text to be added
    to accion field in log.

    Parameters
    -----------
    isprivate = str
        status field value in Project object.

    Returns
    --------
    status = str
        text to be added on accion field Historylogger.
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
    accions: list str
        list of string with the text to be added on accions field on 
        HistoryLogger.

    """
    accions = []
    class_name = instance.__class__.__name__
    for field, value in accions_dic[class_name].iteritems():
        if not instance.__dict__.get(field) == obj.__dict__.get(field):
            try:
                accion = value                
                if field == 'isprivate' and class_name == 'Project':
                    accion = accion + checkIsPrivate(field)
                if field == 'status' and class_name == 'Observation':
                    accion = accion + checkObservationStatus(instance.__dict__.get(field))
                if field == 'status' and class_name == 'Category':
                    accion = accion + checkCategoryStatus(instance.__dict__.get(field))
                if field == 'status' and 'Field' in class_name:
                    accion = accion + checkFieldStatus(instance.__dict__.get(field))
                accions.append(accion)
            except:
                pass
    return accions

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
    print "log_updates", LoggerHistory.objects.last().id,  LoggerHistory.objects.last().accion, LoggerHistory.objects.last().project_id

"""
Receiver for post_save and get creations.
""" 
@receiver(post_save)
def log_created(sender, instance, created, **kwargs):
    if sender.__name__ in list_of_models:
        if created:
            create_log(sender, instance, [sender.__name__+" created"])
    print "log_created", LoggerHistory.objects.last().id,  LoggerHistory.objects.last().accion, LoggerHistory.objects.last().project_id


"""
Receiver for post_deletes for UserGroup, Field and Subset
""" 
@receiver(post_delete) 
def log_delete(sender, instance, *args,  **kwargs):
    try:
        instance.__class__.objects.get(pk=instance.id)
    except:
        if 'Field' == sender.__name__:
            LoggerHistory.objects.create(
                        timestamp=datetime.datetime.now(),
                        project_id=instance.category.project.id,
                        accion="Field deleted",
            )
        if sender.__name__   == 'UserGroup':
            LoggerHistory.objects.create(
                        timestamp=datetime.datetime.now(),
                        project_id=instance.project.id,
                        accion="Usergroup deleted",
            )
        if sender.__name__   == 'Subset':
            LoggerHistory.objects.create(
                        timestamp=datetime.datetime.now(),
                        project_id=instance.project.id,
                        accion="Subset deleted",
            )



# def create_update_log(instance, sender, obj):
#     print "CREATE LOG"
#     accions = cross_check_fields(instance, obj)
#     if accions:
#         for accion in accions:
#             try:
#                 create_log(sender, instance, accion)
#             except:
#                 print "ERROR, something wrong happend"
#                 pass
#             # log = LoggerHistory(
#             #     timestamp=datetime.datetime.now(),
#             #     project_id=0,
#             #     accion=accion
#             #     )
#             # if sender.__name__ == 'User':
#             #     log.user_id = instance.id
#             # if sender.__name__ == 'Project':
#             #     log.project_id = instance.id
#             #     log.user_id = instance.creator.id
#             # if sender.__name__ == 'Comment':
#             #     log.project_id = instance.commentto.project.id
#             #     log.user_id = instance.creator.id
#             # if sender.__name__ == 'Observation':
#             #     log.project_id = instance.project.id
#             #     log.user_id = instance.creator.id
#             # if sender.__name__ == 'UserGroup':
#             #     log.project_id = instance.project.id
#             #     #log.user_id = instance.creator.id
#             # if sender.__name__ == 'Category':
#             #     log.category_id = instance.id
#             #     log.project_id = instance.project.id
#             #     log.user_id = instance.creator.id
#             # if sender.__name__ == 'Subset':
#             #     log.category_id = instance.id
#             #     log.project_id = instance.project.id
#             #     log.user_id = instance.creator.id
#             # if 'Field' in sender.__name__:
#             #     log.project_id = instance.category.project.id
#             #     log.user_id = instance.category.creator.id
#             #     log.category_id = instance.id
#             # log.save()
#     # else:
#     #     accion = cross_check_fields(instance, obj)
#     #     if not accion == False:
#     #         log = LoggerHistory(timestamp=datetime.datetime.now())
#     #         log.accion = accion
#     #         log.project_id = instance.project.id
#     #         log.user_id = instance.creator.id
#     #         log.save()

# # RECEIVER FOR CREATE ##
# @receiver(post_save)
# def log_created(sender, instance, created, **kwargs):
#     print "CREATED", sender.__name__
#     if sender.__name__ in list_of_models:
#         print "\tdentro con ", sender.__name__
#         if created:
#             create_log(sender, instance, sender.__name__+" created")
#             # log = LoggerHistory.objects.create(project_id=0)
#             # log.timestamp = datetime.datetime.now()
#             # log.accion = sender.__name__+" created"
#             # if sender.__name__ == 'User':
#             #     log.user_id = instance.id
#             # if sender.__name__ == 'Project':
#             #     log.project_id = instance.id
#             #     log.user_id = instance.id
#             # if sender.__name__ == 'UserGroup':        
#             #     log.project_id=instance.project.id
#             #     #log.user_id = instance.user.id ## what should be write here
#             # if sender.__name__ == 'Comment':
#             #     log.project_id = instance.commentto.project.id
#             #     log.user_id = instance.creator.id
#             #     log.category_id = instance.commentto.id
#             # if sender.__name__ == "Observation":
#             #     log.categorory_id = instance.id
#             #     log.project_id = instance.project.id
#             #     log.user_id = instance.creator.id
#             #     log.geometry = instance.location.geometry
#             # if sender.__name__ == 'Category':
#             #     log.project_id = instance.project.id
#             #     log.user_id = instance.creator.id
#             #     log.category_id = instance.id
#             # if sender.__name__ == 'Subset':
#             #     log.project_id = instance.project.id
#             #     log.user_id = instance.creator.id
#             # if 'Field' in sender.__name__:
#             #     log.project_id = instance.category.project.id
#             #     log.user_id = instance.category.creator.id
#             #     log.category_id = instance.id
#             #     log.accion = 'Field created'
#             # log.save()