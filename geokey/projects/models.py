from django.db import models
from django.conf import settings
from django.contrib.gis.db import models as gis
from django.core import mail
from django.template.loader import get_template
from django.template import Context
from django.contrib.sites.models import Site

from .manager import ProjectManager
from .base import STATUS, EVERYONE_CONTRIB


class Project(models.Model):
    """
    Stores a single project.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    isprivate = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    everyone_contributes = models.CharField(
        choices=EVERYONE_CONTRIB,
        default=EVERYONE_CONTRIB.auth,
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
    geographic_extend = gis.PolygonField(null=True, geography=True)

    objects = ProjectManager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return '%s status: %s private: %s' % (
            self.name, self.status, self.isprivate)

    @classmethod
    def create(cls, name, description, isprivate, everyone_contributes,
               creator):
        """
        Creates a new project. Creates two usergroups and adds the creator to
        the administrators user group.

        name : str
            Name of the project
        description : str
            Long-form description of the project
        isprivate : Boolean
            Indicates if the project should be private
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
            creator=creator,
            everyone_contributes=everyone_contributes
        )

        project.save()
        Admins.objects.create(project=project, user=creator)

        return project

    def delete(self):
        """
        Deletes the project by setting its status to `DELETED`. Also deletes
        all Admin groups related to the project.
        """
        Admins.objects.filter(project=self).delete()
        self.status = STATUS.deleted
        self.save()

    def re_order_categories(self, order):
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
            not self.isprivate and
            self.groupings.filter(isprivate=False).exists()
            ) or (
            not user.is_anonymous() and (
                self.usergroups.filter(
                    can_contribute=True, users=user).exists() or
                self.usergroups.filter(
                    can_moderate=True, users=user).exists() or
                self.usergroups.filter(
                    users=user, viewgroups__isnull=False).exists())
            )
        )

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
            (self.everyone_contributes != 'false' and (
                not user.is_anonymous() or
                not self.everyone_contributes == 'auth')
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

    def get_all_contributions(self, user):
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
        data = None
        if self.is_admin(user):
            # Return everything for admins
            return self.observations.for_moderator(user)
        elif self.can_moderate(user):
            data = self.observations.for_moderator(user)
        else:
            data = self.observations.for_viewer(user)

        grouping_queries = [
            grouping.get_where_clause()
            for grouping in self.groupings.get_list(user, self.id)
        ]
        grouping_queries = [x for x in grouping_queries if x is not None]

        # Return everything found in data groupings plus the user's data
        if len(grouping_queries) > 0:
            query = '(' + ') OR ('.join(grouping_queries) + ')'

            if (not user.is_anonymous()):
                query = query + ' OR (creator_id = ' + str(user.id) + ')'

            return data.extra(where=[query])

        # If there are no data groupings for the user, return just the user's
        # data
        if (not user.is_anonymous()):
            return self.observations.filter(creator=user)
        else:
            return self.observations.none()

    def contact_admins(self, sender, mail_content):
        """
        Sends an email with `mail_content` to all admins of the project, that
        are contact persons.

        Parameters
        ----------
        sender : str
            Email address of the user sending the request
        mail_content : str
            Email text of the request
        """
        messages = []
        email_text = get_template('contact_admins_email.txt')

        platform = Site.objects.get(pk=settings.SITE_ID).name

        for contact_admin in Admins.objects.filter(project=self, contact=True):
            context = Context({
                'sender': sender,
                'admin': contact_admin.user,
                'email_text': mail_content,
                'project_name': self.name,
                'platform': platform
            })
            text = email_text.render(context)

            email = mail.EmailMessage(
                'Enquiry from %s' % sender.display_name,
                text,
                sender.email,
                [contact_admin.user.email]
            )
            messages.append(email)

        if len(messages) > 0:
            connection = mail.get_connection()
            connection.open()
            connection.send_messages(messages)
            connection.close()


class Admins(models.Model):
    """
    An Administator group for a project. Represents the relation between
    Project and User.
    """
    project = models.ForeignKey('Project', related_name='admin_of')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='has_admins'
    )
    contact = models.BooleanField(default=True)

    class Meta:
        ordering = ['project__name']
        unique_together = ('project', 'user')
