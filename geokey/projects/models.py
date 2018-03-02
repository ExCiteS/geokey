"""Models for projects."""

from django.db import models
from django.conf import settings
from django.contrib.gis.db import models as gis

from geokey.core import signals
from simple_history.models import HistoricalRecords

from .managers import ProjectManager
from .base import STATUS, EVERYONE_CONTRIBUTES


class Project(models.Model):
    """
    Stores a single project.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    isprivate = models.BooleanField(default=False)
    islocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    everyone_contributes = models.CharField(
        choices=EVERYONE_CONTRIBUTES,
        default=EVERYONE_CONTRIBUTES.auth,
        max_length=20
    )
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )
    admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='admins',
        through='Admins'
    )
    geographic_extent = gis.PolygonField(null=True, geography=True)

    objects = ProjectManager()
    history = HistoricalRecords()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return '%s status: %s private: %s' % (
            self.name, self.status, self.isprivate)

    @classmethod
    def create(cls, name, description, isprivate, islocked,
               everyone_contributes, creator):
        """
        Creates a new project and adds the creator to
        the administrators user group.

        name : str
            Name of the project
        description : str
            Long-form description of the project
        isprivate : Boolean
            Indicates if the project should be private
        islocked : Boolean
            Indicates if the project should be locked
        everyone_contributes : str
            Indicates if all you users who have access can contribute to the
            project

            Accepted:
            true - all users who have access, including anonymous
            auth - all user who are authenticated
            false - users need to be member of a user group

        Return
        ------
        geokey.projects.models.Project
        """
        project = cls(
            name=name,
            description=description,
            isprivate=isprivate,
            islocked=islocked,
            creator=creator,
            everyone_contributes=everyone_contributes
        )

        project.save()
        Admins.objects.create(project=project, user=creator)

        return project

    def save(self, *args, **kwargs):
        """
        Checks if project is set to private, but everyone_contributes is set
        to `TRUE` and makes the option set to `AUTH`.

        We are not allowing anonymous contributions for private projects.
        """
        if (self.isprivate and
                self.everyone_contributes == EVERYONE_CONTRIBUTES.true):
            self.everyone_contributes = EVERYONE_CONTRIBUTES.auth

        super(Project, self).save(*args, **kwargs)

    def delete(self):
        """
        Deletes the project by setting its status to `DELETED`. Also deletes
        all Admin groups related to the project.
        """
        Admins.objects.filter(project=self).delete()
        signals.delete_project.send(sender=Project, project=self)
        self.status = STATUS.deleted
        self.save()

    def reorder_categories(self, order):
        """
        Reorders the categories according to the order given in `order`

        Parameters
        ----------
        order : list
            ordered list of category IDs that define the new order
        """
        categories_to_save = []
        for idx, category_id in enumerate(order):
            category = self.categories.get(pk=category_id)
            category.order = idx
            categories_to_save.append(category)

        for category in categories_to_save:
            category.save()

    def get_role(self, user):
        """
        Returns the user's role in plain text

        Parameters
        ----------
        user : geokey.users.models.User
            User that is examined

        Returns
        -------
        str
            Role of the user in the project
        """
        if self.is_admin(user):
            return 'administrator'
        elif self.can_moderate(user):
            return 'moderator'
        elif self.can_contribute(user):
            return 'contributor'
        else:
            return 'watcher'

    def is_admin(self, user):
        """
        Returns True if the user is member of the administrators group, False
        if not.

        Parameters
        ----------
        user : geokey.users.models.User
            User that is examined

        Returns
        -------
        Boolean
            Indicating if user is admin
        """
        return user in self.admins.all()

    def can_access(self, user):
        """
        Returns True if:
        - the user is member of the administrators group
        - the user is member of one of the usergroups
        - the project is public and has at least one public data grouping

        Parameters
        ----------
        user : geokey.users.models.User
            User that is examined

        Returns
        -------
        Boolean
            Indicating if user is can access
        """
        return self.status == STATUS.active and (self.is_admin(user) or (
            not self.isprivate) or (
            not user.is_anonymous() and (
                self.usergroups.filter(
                    can_contribute=True, users=user).exists() or
                self.usergroups.filter(
                    can_moderate=True, users=user).exists())
        ))

    def can_contribute(self, user):
        """
        Returns True if:
        - the user is member of the administrators group
        - the user is member of one usergroup that has can_contribute granted
        - everyone_contributes is True

        Parameters
        ----------
        user : geokey.users.models.User
            User that is examined

        Returns
        -------
        Boolean
            Indicating if user can contribute
        """
        return self.status == STATUS.active and (
            (self.everyone_contributes != EVERYONE_CONTRIBUTES.false and (
                not user.is_anonymous() or
                not self.everyone_contributes == EVERYONE_CONTRIBUTES.auth)
             ) or self.is_admin(user) or (
                not user.is_anonymous() and (
                    self.usergroups.filter(
                        can_contribute=True, users=user).exists())))

    def can_moderate(self, user):
        """
        Returns True if the user is member of a user group with moderation
        rights

        Parameters
        ----------
        user : geokey.users.models.User
            User that is examined

        Returns
        -------
        Boolean
            Indicating if user can moderate
        """
        return self.status == STATUS.active and (
            self.is_admin(user) or (
                not user.is_anonymous() and (
                    self.usergroups.filter(
                        can_moderate=True, users=user).exists())))

    def is_involved(self, user):
        """
        Returns True if:
        - the user is member of the administrators group
        - the user is member of at least usergroup assigned to the project

        Parameters
        ----------
        user : geokey.users.models.User
            User that is examined

        Returns
        -------
        Boolean
            Indicating if user is involved
        """
        return self.is_admin(user) or (
            not user.is_anonymous() and (
                self.usergroups.filter(users=user).exists()))

    def get_all_contributions(self, user, search=None, subset=None, bbox=None):
        """
        Returns all contributions a user can access in a project. It gets
        the SQL clauses of all data groupings in the project and combines them
        to filter all contributions in the project.

        Parameters
        ----------
        user : geokey.users.models.User
            User that contributions are queried for

        Returns
        -------
        django.db.models.query.QuerySet
            List of geokey.contributions.models.Observations
        """
        is_admin = self.is_admin(user)
        data = self.observations

        if is_admin or self.can_moderate(user):
            data = data.for_moderator(user)
        else:
            data = data.for_viewer(user)

        where_clause = None
        if not is_admin and self.isprivate and not user.is_anonymous():
            clauses = []

            for group in self.usergroups.filter(users=user):
                if group.where_clause is not None:
                    clauses.append(group.where_clause)

            if clauses:
                where_clause = '(' + ') OR ('.join(clauses) + ')'

        if subset:
            sub = self.subsets.get(pk=subset)
            if where_clause:
                where_clause = '(' + sub.where_clause + ') AND ' + where_clause
            else:
                where_clause = sub.where_clause

        if where_clause:
            data = data.extra(where=[where_clause])

        if search:
            data = data.search(search)

        if bbox:
            data = data.get_by_bbox(bbox)

        return data.distinct()


class Admins(models.Model):
    """
    An Administator group for a project. Represents the relation between
    Project and User.
    """
    objects = None
    project = models.ForeignKey('Project', related_name='admin_of')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='has_admins'
    )

    class Meta:
        ordering = ['project__name']
        unique_together = ('project', 'user')
