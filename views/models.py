from django.db import models
from django.conf import settings

from model_utils import Choices

STATUS = Choices('active', 'inactive', 'deleted')


class View(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )
    project = models.ForeignKey('projects.Project', related_name='views')

    def delete(self):
        """
        Deletes the view by setting its status to DELETED.
        """
        self.status = STATUS.deleted
        self.save()


class Viewgroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    can_edit = models.BooleanField(default=False)
    can_read = models.BooleanField(default=False)
    can_view = models.BooleanField(default=True)
    view = models.ForeignKey('View')
