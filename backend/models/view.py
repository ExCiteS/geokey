from django.db import models

from django.conf import settings

from .choice import STATUS_TYPES
from .managers import Manager


class View(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(default=STATUS_TYPES['ACTIVE'])
    project = models.ForeignKey('backend.Project')

    objects = Manager()

    class Meta:
        app_label = 'backend'

    def update(self, name=None, description=None):
        """
        Updates a view.
        """

        if (name):
            self.name = name
        if (description):
            self.description = description

        self.save()

    def delete(self):
        """
        Deletes the view by setting its status to DELETED.
        """
        self.status = STATUS_TYPES['DELETED']
        self.save()

    def isViewable(self, user):
        """
        Checks if the View is viewable by the user
        """
        if self.project.admins.isMember(user):
            return True
        else:
            canView = False
            for group in self.viewgroup_set.all():
                if group.isMember(user):
                    canView = True

            return canView

    def _check_permission(self, user, access_type):
        can_do = False
        for group in self.viewgroup_set.filter(
            users__id__exact=user.id
        ).values():
            if group[access_type]:
                can_do = True

        return can_do
