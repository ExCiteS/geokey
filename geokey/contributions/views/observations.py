from django.core.exceptions import PermissionDenied

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from geokey.core.decorators import handle_exceptions_for_ajax
from geokey.users.models import User
from geokey.projects.models import Project
from geokey.datagroupings.models import Grouping
from geokey.datagroupings.serializers import GroupingSerializer

from .base import (
    SingleAllContribution, SingleGroupingContribution, SingleMyContribution
)
from ..serializers import ContributionSerializer


class ProjectObservations(APIView):
    """
    Public API endpoint to add new contributions to a project
    /api/projects/:project_id/contributions
    """
    @handle_exceptions_for_ajax
    def post(self, request, project_id):
        """
        Adds a new contribution to a project

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request
        project_id : int
            identifies the project in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised contribution
        """
        user = request.user
        if user.is_anonymous():
            user = User.objects.get(display_name='AnonymousUser')

        data = request.DATA
        project = Project.objects.as_contributor(request.user, project_id)

        if (not data.get('meta').get('status') == 'draft' and
                project.can_moderate(user)):
            data['meta']['status'] = 'active'

        serializer = ContributionSerializer(
            data=data, context={'user': user, 'project': project}
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class ContributionSearchAPIView(APIView):
    """
    Public API endpoint to search all contributions in a project
    /api/projects/:project_id/contributions/search/?query={query}
    """
    @handle_exceptions_for_ajax
    def get(self, request, project_id):
        """
        Returns a list of contributions that match the query

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request
        project_id : int
            identifies the project in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised search results
        """
        q = request.GET.get('query')

        project = Project.objects.get_single(request.user, project_id)
        contributions = project.get_all_contributions(request.user).search(q)

        serializer = ContributionSerializer(
            contributions,
            many=True,
            context={'user': request.user, 'project': project, 'search': q}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class ProjectObservationsView(APIView):
    """
    Public API endpoint to get all contributions in a project
    /api/projects/:project_id/data-groupings/all-contributions/
    """
    @handle_exceptions_for_ajax
    def get(self, request, project_id):
        """
        Returns a list of contributions for a project

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request
        project_id : int
            identifies the project in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised observations
        """
        project = Project.objects.get_single(request.user, project_id)
        contributions = project.get_all_contributions(request.user)

        serializer = ContributionSerializer(
            contributions,
            many=True,
            context={'user': request.user, 'project': project}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyObservations(APIView):
    """
    Public API endpoint for user's observations in a project.
    /api/projects/:project_id/data-groupings/my-contributions/
    """

    @handle_exceptions_for_ajax
    def get(self, request, project_id):
        """
        Returns a list of user's contributions

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request
        project_id : int
            identifies the project in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised observations
        """
        project = Project.objects.get_single(request.user, project_id)

        if request.user.is_anonymous():
            return Response(
                {"error": "You need to login to view your contributions."},
                status=status.HTTP_404_NOT_FOUND
            )

        if project.can_contribute(request.user):
            observations = project.observations.filter(creator=request.user)

            serializer = ContributionSerializer(
                observations,
                many=True,
                context={'user': request.user, 'project': project}
            )
            return Response(serializer.data)
        else:
            return Response(
                {"error": "You are not a contributor of this project."},
                status=status.HTTP_404_NOT_FOUND
            )


class ViewObservations(APIView):
    """
    Public API endpoint for all observations in data grouping.
    /api/projects/:project_id/data-groupings/:grouping_id/
    """
    @handle_exceptions_for_ajax
    def get(self, request, project_id, grouping_id):
        """
        Returns a single view and its data
        /api/projects/:project_id/data-groupings/:grouping_id/

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request
        project_id : int
            identifies the project in the data base
        grouping_id : int
            identifies the data grouping in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised observations
        """
        view = Grouping.objects.get_single(
            request.user,
            project_id,
            grouping_id
        )
        serializer = GroupingSerializer(view, context={'user': request.user})
        return Response(serializer.data)


# ############################################################################
#
# SINGLE CONTRIBUTIONS
#
# ############################################################################


class SingleContributionAPIView(APIView):
    """
    Abstract APIView for handling requests to single observations
    """
    def get_and_respond(self, request, observation):
        """
        Returns a single contributions

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request
        observation : geokey.contributions.models.Observation
            Observation to be returned

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised observation
        """
        serializer = ContributionSerializer(
            observation,
            context={'user': request.user, 'project': observation.project}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update_and_respond(self, request, observation):
        """
        Updates and returns a single contributions

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request
        observation : geokey.contributions.models.Observation
            Observation to be returned

        Returns
        -------
        rest_framework.response.Respone
            Contains the updated serialised observation
        """
        data = request.DATA
        user = request.user
        if user.is_anonymous():
            user = User.objects.get(display_name='AnonymousUser')

        new_status = None
        if data.get('meta') is not None:
            new_status = data.get('meta').get('status')

        user_can_moderate = observation.project.can_moderate(user)
        user_is_owner = (observation.creator == user)
        under_review = observation.comments.filter(
            review_status='open').exists()

        if (new_status is not None and new_status != observation.status):
            if not (
                (new_status == 'pending' and
                    (user_is_owner or user_can_moderate)) or
                (new_status == 'active' and
                    observation.status == 'draft' and user_is_owner) or
                (new_status == 'active' and
                    observation.status == 'pending' and user_can_moderate)):

                raise PermissionDenied('You are not allowed to update the '
                                       'status of the contribution from "%s" '
                                       'to "%s"' % (
                                           observation.status,
                                           new_status
                                       ))

        elif not (user_is_owner or user_can_moderate):
            raise PermissionDenied('You are not allowed to update the'
                                   'contribution')

        if new_status == 'active' and under_review:
            data['meta']['status'] = 'review'

        if ((new_status == 'active' and observation.status == 'draft') and
                not user_can_moderate):
            default_status = observation.category.default_status
            data['meta']['status'] = default_status

        serializer = ContributionSerializer(
            observation,
            data=data,
            context={'user': user, 'project': observation.project}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    def delete_and_respond(self, request, observation):
        """
        Deletes a single observation

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request
        observation : geokey.contributions.models.Observation
            Observation to be deleted

        Returns
        -------
        rest_framework.response.Respone
            Empty response indicating successful delete
        """
        if (observation.creator == request.user or
                observation.project.can_moderate(request.user)):
            observation.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        raise PermissionDenied('You are not allowed to delete this'
                               'contribution')


class SingleAllContributionAPIView(
        SingleAllContribution, SingleContributionAPIView):
    """
    Public API endpoint for updating a single observation in a project
    /api/projects/:project_id/observations/:observation_id
    """

    @handle_exceptions_for_ajax
    def get(self, request, project_id, observation_id):
        """
        Returns a single contribution

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised observation
        """
        observation = self.get_object(request.user, project_id, observation_id)
        return self.get_and_respond(request, observation)

    @handle_exceptions_for_ajax
    def patch(self, request, project_id, observation_id):
        """
        Updates and returns a single contribution

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the updated serialised observation
        """
        observation = self.get_object(request.user, project_id, observation_id)
        return self.update_and_respond(request, observation)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, observation_id):
        """
        Deletes a single contribution

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Empty response indicating successful delete
        """
        observation = self.get_object(request.user, project_id, observation_id)
        return self.delete_and_respond(request, observation)


class SingleGroupingContributionAPIView(
        SingleGroupingContribution, SingleContributionAPIView):
    """
    Public API endpoint for updating a single observation in a project
    /api/projects/:project_id/views/:grouping_id/observations/:observation_id
    """
    @handle_exceptions_for_ajax
    def get(self, request, project_id, grouping_id, observation_id):
        """
        Returns a single contribution

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request
        project_id : int
            identifies the project in the data base
        grouping_id : int
            identifies the data grouping in the data base
        observation_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised observation
        """
        observation = self.get_object(
            request.user, project_id, grouping_id, observation_id)
        return self.get_and_respond(request, observation)

    @handle_exceptions_for_ajax
    def patch(self, request, project_id, grouping_id, observation_id):
        """
        Updates and returns a single contribution

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request
        project_id : int
            identifies the project in the data base
        grouping_id : int
            identifies the data grouping in the data base
        observation_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the updated serialised observation
        """
        observation = self.get_object(
            request.user, project_id, grouping_id, observation_id)
        return self.update_and_respond(request, observation)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, grouping_id, observation_id):
        """
        Deletes a single contribution

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request
        project_id : int
            identifies the project in the data base
        grouping_id : int
            identifies the data grouping in the data base
        observation_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Empty response indicating successful delete
        """
        observation = self.get_object(
            request.user, project_id, grouping_id, observation_id)
        return self.delete_and_respond(request, observation)


class SingleMyContributionAPIView(
        SingleMyContribution, SingleContributionAPIView):

    @handle_exceptions_for_ajax
    def get(self, request, project_id, observation_id):
        """
        Returns a single contribution

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised observation
        """
        observation = self.get_object(request.user, project_id, observation_id)
        return self.get_and_respond(request, observation)

    @handle_exceptions_for_ajax
    def patch(self, request, project_id, observation_id):
        """
        Updates and returns a single contribution

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the updated serialised observation
        """
        observation = self.get_object(request.user, project_id, observation_id)
        return self.update_and_respond(request, observation)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, observation_id):
        """
        Deletes a single contribution

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Empty response indicating successful delete
        """
        observation = self.get_object(request.user, project_id, observation_id)
        return self.delete_and_respond(request, observation)
