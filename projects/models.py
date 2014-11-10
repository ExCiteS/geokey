from django.db import models
from django.conf import settings
from django.contrib.gis.db import models as gis
from django.core import mail
from django.template.loader import get_template
from django.template import Context

from .manager import ProjectManager
from .base import STATUS


class Project(models.Model):
    """
    Stores a single project.
    """

    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    isprivate = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    everyone_contributes = models.BooleanField(default=True)
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
        Removes the project from the listing of all projects by setting its
        status to `DELETED`.
        """
        self.status = STATUS.deleted
        self.save()

    def get_role(self, user):
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
        """
        return user in self.admins.all()

    def can_access(self, user):
        """
        Returns True if:
        - the user is member of the administrators group
        - the user is member of one of the usergroups
        - the project is public and has at least one public view
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
        """
        return self.status == STATUS.active and (
            self.everyone_contributes or self.is_admin(user) or (
                not user.is_anonymous() and (
                    self.usergroups.filter(
                        can_contribute=True, users=user).exists())))

    def can_moderate(self, user):
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
        """
        return self.is_admin(user) or (
            not user.is_anonymous() and (
                self.usergroups.filter(users=user).exists()))

    def get_all_contributions(self, user):
        """
        Returns all contributions a user can access in a project
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
        """
        messages = []
        email_text = get_template('contact_admins_email.txt')

        for contact_admin in Admins.objects.filter(project=self, contact=True):
            context = Context({
                'sender': sender,
                'admin': contact_admin.user,
                'email_text': mail_content,
                'project_name': self.name,
                'platform': settings.PLATFORM_NAME
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
    project = models.ForeignKey('Project', related_name='admin_of')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='has_admins'
    )
    contact = models.BooleanField(default=True)

    class Meta:
        ordering = ['project__name']
        unique_together = ('project', 'user')
