"""Base for views of contributions."""

from geokey.projects.models import Project


class SingleAllContribution(object):
    """Base class for a single contribution of all contributions."""

    def get_object(self, user, project_id, contribution_id):
        """
        Get a single contribution.

        Parameters
        ----------
        user : geokey.users.models.User
            User requesting the request.
        project_id : int
            Identifies the project in the database.
        contribution_id : int
            Identifies the contribution in the database.

        Returns
        -------
        geokey.contributions.models.Observation

        Raises
        ------
        Observation.DoesNotExist
            If the object was not found or is not accessible by the user.
        """
        project = Project.objects.get_single(user, project_id)

        if project.can_moderate(user):
            return project.get_all_contributions(
                user).for_moderator(user).get(pk=contribution_id)
        else:
            return project.get_all_contributions(
                user).for_viewer(user).get(pk=contribution_id)
