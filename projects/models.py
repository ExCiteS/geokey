from django.db import models
from django.conf import settings
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from model_utils import Choices


STATUS = Choices('active', 'inactive', 'deleted')


class ProjectQuerySet(models.query.QuerySet):
    def for_user(self, user, pk=None):
        return self.filter(
            Q(admins__users=user) |
            (
                Q(status=STATUS.active) &
                (Q(isprivate=False) | Q(contributors__users=user))
            )
        ).distinct()


class ProjectManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return ProjectQuerySet(self.model).exclude(status=STATUS.deleted)

    def for_user(self, user):
        return self.get_query_set().for_user(user)

    def get(self, user, pk):
        project = super(ProjectManager, self).get(pk=pk)
        if user in project.admins.users.all() or (
            (not project.isprivate or user in project.contributors.users.all())
            and project.status != STATUS.inactive
        ):
            return project
        else:
            raise PermissionDenied('Not allowed')


class Project(models.Model):
    """
    Stores a single project. Extends `Authenticatable`.
    """

    name = models.CharField(max_length=100)
    description = models.TextField()
    isprivate = models.BooleanField(default=False)
    everyonecontributes = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )
    admins = models.OneToOneField(
        'UserGroup', related_name='admingroup'
    )
    contributors = models.OneToOneField(
        'UserGroup', related_name='contributorgroup'
    )

    objects = ProjectManager()

    def __str__(self):
        return self.name + ' status: ' + self.status + ' private: ' + str(self.isprivate)

    @classmethod
    def create(cls, name, description, isprivate, creator):
        """
        Creates a new project. Creates two usergroups and adds the creator to
        the administrators user group.
        """
        admingroup = UserGroup.objects.create(name='Administrators')
        admingroup.users.add(creator)

        contributorgroup = UserGroup.objects.create(name='Contributors')

        return cls(
            name=name,
            description=description,
            isprivate=isprivate,
            creator=creator,
            admins=admingroup,
            contributors=contributorgroup
        )

    def delete(self):
        """
        Removes the project from the listing of all projects by setting its
        status to `DELETED`.
        """
        self.status = STATUS.deleted
        self.save()


class UserGroup(models.Model):
    """
    UserGroup for a project, either Administrators or contributors
    """

    name = models.CharField(max_length=100)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
