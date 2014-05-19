from django.db import models
from django.conf import settings

from .manager import ProjectManager
from .base import STATUS


class Project(models.Model):
    """
    Stores a single project.
    """

    name = models.CharField(max_length=100)
    description = models.TextField()
    isprivate = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='admins')

    objects = ProjectManager()

    def __str__(self):
        return self.name + ' status: ' + self.status + ' private: ' + str(self.isprivate)

    @classmethod
    def create(cls, name, description, isprivate, creator):
        """
        Creates a new project. Creates two usergroups and adds the creator to
        the administrators user group.
        """

        project = cls(
            name=name,
            description=description,
            isprivate=isprivate,
            creator=creator
        )

        project.save()
        project.admins.add(creator)

        return project

    def delete(self):
        """
        Removes the project from the listing of all projects by setting its
        status to `DELETED`.
        """
        self.status = STATUS.deleted
        self.save()

    def is_admin(self, user):
        """
        Returns True if the user is member of the administrators group, False
        if not.
        """
        return user in self.admins.all()

    def can_access(self, user):
        """
        Returns True if the user is either member of the administrators group
        -if active- the contributors group or one the Viewgroups of the
        project.
        """
        return self.status == STATUS.active and (self.is_admin(user) or (
            (not self.isprivate or
                self.usergroups.filter(can_contribute=True, users=user).exists() or
                self.views.filter(viewgroups__users=user).exists())))

    def can_contribute(self, user):
        return self.status == STATUS.active and (
            self.is_admin(user) or (
                self.usergroups.filter(can_contribute=True, users=user).exists()
            ))
