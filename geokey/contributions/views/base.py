from geokey.projects.models import Project
from geokey.datagroupings.models import Grouping
from geokey.contributions.models import Observation


class SingleAllContribution(object):
    """
    Base class for single contributions on the all contributions endpoints
    """
    def get_object(self, user, project_id, observation_id):
        """
        Returns a single Obervation

        Parameters
        ----------
        user : geokey.users.models.User
            User requesting the contribution
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base

        Returns
        -------
        geokey.contributions.models.Observation

        Raises
        ------
        Observation.DoesNotExist
            If the observations was not found or is not accessible by the user
        """
        project = Project.objects.get_single(user, project_id)

        if project.can_moderate(user):
            return project.get_all_contributions(
                user).for_moderator(user).get(pk=observation_id)
        else:
            return project.get_all_contributions(
                user).for_viewer(user).get(pk=observation_id)


class SingleGroupingContribution(object):
    """
    Base class for single contributions on the data groupings endpoints
    """
    def get_object(self, user, project_id, grouping_id, observation_id):
        """
        Returns a single Obervation

        Parameters
        ----------
        user : geokey.users.models.User
            User requesting the contribution
        project_id : int
            identifies the project in the data base
        grouping_id : int
            identifies the data grouping in the data base
        observation_id : int
            identifies the observation in the data base

        Returns
        -------
        geokey.contributions.models.Observation

        Raises
        ------
        Observation.DoesNotExist
            If the observations was not found or is not accessible by the user
        """
        view = Grouping.objects.get_single(user, project_id, grouping_id)
        return view.data(user).get(pk=observation_id)


class SingleMyContribution(object):
    """
    Base class for single contributions on the user contributions endpoints
    """
    def get_object(self, user, project_id, observation_id):
        """
        Returns a single Obervation

        Parameters
        ----------
        user : geokey.users.models.User
            User requesting the contribution
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base

        Returns
        -------
        geokey.contributions.models.Observation

        Raises
        ------
        Observation.DoesNotExist
            If the observations was not found or is not accessible by the user
        """
        observation = Project.objects.get_single(
            user, project_id).observations.get(pk=observation_id)

        if observation.creator == user:
            return observation
        else:
            raise Observation.DoesNotExist('You are not the creator of this '
                                           'contribution or the contribution '
                                           'has been deleted.')
