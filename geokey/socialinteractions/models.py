"""Models for subsets."""

from django.conf import settings
from django.db import models

from allauth.socialaccount.models import SocialAccount


class SocialInteraction(models.Model):
    """Stores a single social interaction."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    project = models.ForeignKey(
        'projects.Project',
        related_name='socialinteractions'
    )
    socialaccounts = models.ManyToManyField(
        SocialAccount,
        related_name='socialinteractions',
        through='SocialAccounts'
    )

    @classmethod
    def create(cls, name, description, project, socialaccounts, creator):
        """
        Creates a new social interaction and adds the creator and selected
        social accounts asociated to this project

        name : str
            Name of the project
        description : str
            Long-form description of the project
        project : project object
            project object
        socialaccounts : list
            list of social accounts ids associated to this social interaciton
        creator : str
            Indicates if all you users who have access can contribute to the
            project

            Accepted:
            true - all users who have access, including anonymous
            auth - all user who are authenticated
            false - users need to be member of a user group

        Return
        ------
        geokey.socialinteractions.models.SocialInteraction
        """
        if socialaccounts:
            socialinteraction = cls(
                name=name,
                description=description,
                project=project,
                creator=creator
            )

            socialinteraction.save()

            for sa in socialaccounts:
                socialinteraction.socialaccounts.add(sa)

            return socialinteraction
        else:
            return

    def update(self, socialinteraction_id, name, description, socialaccounts):
        """
        Updates social interaction

        Parameters
        -----------
        socialinteraction_id : int
            UID of the social interaction
        name :  str
            name of the social interaction
        description: str
            long-form description of the social interaction
        socialaccounts: list
            list of socialaccount ids to be added to the social interaction

        returns
        --------
        geokey.socialinteractions.models.SocialInteraction

        """
        if self:

            self.description = description
            self.name = name
            self.save()
            all_socialccounts = self.socialaccounts.all()
            sa_added = [s for s in socialaccounts]
            sa_exist = [i for i in all_socialccounts]
            to_add = set(sa_added) - set(sa_exist)
            to_remove = set(sa_exist) - set(sa_added)

            for sa_id in to_add:
                self.socialaccounts.add(sa_id)
            for sa_id in to_remove:
                self.socialaccounts.remove(sa_id)
        return self


class SocialAccounts(models.Model):
    """Stores a relation between an interaction and account."""
    socialinteraction = models.ForeignKey(
        'SocialInteraction',
        related_name='socialaccount_of'
    )
    socialaccount = models.ForeignKey(
        SocialAccount,
        related_name='has_socialaccount'
    )

    class Meta:
        auto_created = True
        ordering = ['socialinteraction__name']
        unique_together = ('socialinteraction', 'socialaccount')
