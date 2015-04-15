from django.core.exceptions import PermissionDenied

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from geokey.core.exceptions import MalformedRequestData
from geokey.core.decorators import handle_exceptions_for_ajax
from .base import (
    SingleAllContribution, SingleGroupingContribution, SingleMyContribution
)

from geokey.users.models import User
from ..serializers import FileSerializer
from ..models import MediaFile


class MediaFileListAbstractAPIView(APIView):
    """
    Abstract APIView for listing media files of a contribution
    """
    def get_list_and_respond(self, user, contribution):
        """
        Serialises all files attached to the contribution and returns the
        JSON response

        Parameter
        ---------
        user : geokey.users.models.User
            User authenticated with the request
        contribution : geokey.contributions.models.Observation
            contribution the comments are requested for

        Returns
        -------
        rest_framework.response.Respones
            Contains the serialised files
        """
        files = contribution.files_attached.all()
        serializer = FileSerializer(
            files, many=True, context={'user': user})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create_and_respond(self, user, contribution):
        """
        Creates an file and responds with the file information

        Parameter
        ---------
        user : geokey.users.models.User
            User authenticated with the request
        contribution : geokey.contributions.models.Observation
            contribution the comments are requested for

        Returns
        -------
        rest_framework.response.Respones
            Contains the serialised file
        """
        if user.is_anonymous():
            user = User.objects.get(display_name='AnonymousUser')

        data = self.request.POST
        name = data.get('name')
        description = data.get('description')
        the_file = self.request.FILES.get('file')
        errors = []

        if name is None:
            errors.append('Property name is not set.')

        if the_file is None:
            errors.append('No file attached.')

        if errors:
            raise MalformedRequestData(', '.join(errors))

        if contribution.project.can_contribute(user):
            the_file = MediaFile.objects.create(
                name=name,
                description=description,
                contribution=contribution,
                creator=user,
                the_file=the_file
            )

            serializer = FileSerializer(the_file, context={'user': user})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise PermissionDenied('You are not allowed to contribute to the'
                                   'project.')


class AllContributionsMediaAPIView(
        MediaFileListAbstractAPIView, SingleAllContribution):
    """
    View for media file lists on all contributions endpoints
    """

    @handle_exceptions_for_ajax
    def get(self, request, project_id, contribution_id):
        """
        Returns a list of all files attached to the observation

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request
        project_id : int
            identifies the project in the data base
        contribution_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised comments
        """
        contribution = self.get_object(
            request.user,
            project_id,
            contribution_id
        )
        return self.get_list_and_respond(request.user, contribution)

    @handle_exceptions_for_ajax
    def post(self, request, project_id, contribution_id):
        """
        Creates a new file for a contribution

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request
        project_id : int
            identifies the project in the data base
        contribution_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised comments
        """
        contribution = self.get_object(
            request.user,
            project_id,
            contribution_id
        )
        return self.create_and_respond(request.user, contribution)


class MyContributionsMediaApiView(
        MediaFileListAbstractAPIView, SingleMyContribution):
    """
    View for media file lists on my contributions endpoints
    """

    @handle_exceptions_for_ajax
    def get(self, request, project_id, contribution_id):
        """
        Returns a list of all files attached to the observation

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request
        project_id : int
            identifies the project in the data base
        contribution_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised comments
        """
        contribution = self.get_object(
            request.user,
            project_id,
            contribution_id
        )
        return self.get_list_and_respond(request.user, contribution)

    @handle_exceptions_for_ajax
    def post(self, request, project_id, contribution_id):
        """
        Creates a new file for a contribution

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request
        project_id : int
            identifies the project in the data base
        contribution_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised comments
        """
        contribution = self.get_object(
            request.user,
            project_id,
            contribution_id
        )
        return self.create_and_respond(request.user, contribution)


class GroupingContributionsMediaApiView(
        MediaFileListAbstractAPIView, SingleGroupingContribution):
    """
    View for media file lists on data groupings endpoints
    """

    @handle_exceptions_for_ajax
    def get(self, request, project_id, grouping_id, contribution_id):
        """
        Returns a list of all files attached to the observation

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request
        project_id : int
            identifies the project in the data base
        grouping_id : int
            identifies the data grouping in the data base
        contribution_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised comments
        """
        contribution = self.get_object(
            request.user,
            project_id,
            grouping_id,
            contribution_id
        )
        return self.get_list_and_respond(request.user, contribution)

    @handle_exceptions_for_ajax
    def post(self, request, project_id, grouping_id, contribution_id):
        """
        Creates a new file for a contribution

        Parameters
        ----------
        request : rest_framework.request.Request
            Represents the request
        project_id : int
            identifies the project in the data base
        grouping_id : int
            identifies the data grouping in the data base
        contribution_id : int
            identifies the observation in the data base

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised comments
        """
        contribution = self.get_object(
            request.user,
            project_id,
            grouping_id,
            contribution_id
        )
        return self.create_and_respond(request.user, contribution)


class MediaFileSingleAbstractView(APIView):
    """
    Abstract APIView for single file endpoints.
    """
    def get_and_respond(self, user, media_file):
        """
        Returns a single media file

        Parameter
        ---------
        user : geokey.users.models.User
            User authenticated with the request
        media_file : geokey.contributions.models.MediaFile
            File to be returned

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised file
        """
        serializer = FileSerializer(media_file, context={'user': user})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete_and_respond(self, user, media_file):
        """
        Deletes a single media file

        Parameter
        ---------
        user : geokey.users.models.User
            User authenticated with the request
        media_file : geokey.contributions.models.MediaFile
            File to be deleted

        Returns
        -------
        rest_framework.response.Respone
            Empty response stating the success of the delete
        """
        if (media_file.creator == user or
                media_file.contribution.project.can_moderate(user)):
            media_file.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        raise PermissionDenied('You neither are the creator if this file '
                               'nor a project moderator and therefore '
                               'not eligable to delete this file.')


class AllContributionsSingleMediaApiView(
        MediaFileSingleAbstractView, SingleAllContribution):
    """
    APIView for single files on all contributions endpoints
    """

    def get_file(self, user, project_id, contribution_id, file_id):
        """
        Returns the file object

        Parameter
        ---------
        user : geokey.users.models.User
            User authenticated with the request
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base
        file_id : int
            identifies the file in the database

        Returns
        -------
        geokey.contributions.models.MediaFile
        """
        contribution = self.get_object(user, project_id, contribution_id)
        return contribution.files_attached.get(pk=file_id)

    @handle_exceptions_for_ajax
    def get(self, request, project_id, contribution_id, file_id):
        """
        Returns a single media file

        Parameter
        ---------
        user : geokey.users.models.User
            User authenticated with the request
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base
        file_id : int
            identifies the file in the database

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised file
        """
        media_file = self.get_file(
            request.user,
            project_id,
            contribution_id,
            file_id
        )
        return self.get_and_respond(request.user, media_file)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, contribution_id, file_id):
        """
        Deletes a single media file

        Parameter
        ---------
        user : geokey.users.models.User
            User authenticated with the request
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base
        file_id : int
            identifies the file in the database

        Returns
        -------
        rest_framework.response.Respone
            Empty repsonse indicating success
        """
        media_file = self.get_file(
            request.user,
            project_id,
            contribution_id,
            file_id
        )
        return self.delete_and_respond(request.user, media_file)


class MyContributionsSingleMediaApiView(
        MediaFileSingleAbstractView, SingleMyContribution):
    """
    APIView for single files on my contributions endpoints
    """

    def get_file(self, user, project_id, contribution_id, file_id):
        """
        Returns the file object

        Parameter
        ---------
        user : geokey.users.models.User
            User authenticated with the request
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base
        file_id : int
            identifies the file in the database

        Returns
        -------
        geokey.contributions.models.MediaFile
        """
        contribution = self.get_object(user, project_id, contribution_id)
        return contribution.files_attached.get(pk=file_id)

    @handle_exceptions_for_ajax
    def get(self, request, project_id, contribution_id, file_id):
        """
        Returns a single media file

        Parameter
        ---------
        user : geokey.users.models.User
            User authenticated with the request
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base
        file_id : int
            identifies the file in the database

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised file
        """
        media_file = self.get_file(
            request.user,
            project_id,
            contribution_id,
            file_id
        )
        return self.get_and_respond(request.user, media_file)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, contribution_id, file_id):
        """
        Deletes a single media file

        Parameter
        ---------
        user : geokey.users.models.User
            User authenticated with the request
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base
        file_id : int
            identifies the file in the database

        Returns
        -------
        rest_framework.response.Respone
            Empty repsonse indicating success
        """
        media_file = self.get_file(
            request.user,
            project_id,
            contribution_id,
            file_id
        )
        return self.delete_and_respond(request.user, media_file)


class GroupingContributionsSingleMediaApiView(
        MediaFileSingleAbstractView, SingleGroupingContribution):
    """
    APIView for single files on data groupings endpoints
    """

    def get_file(self, user, project_id, grouping_id, contribution_id,
                 file_id):
        """
        Returns the file object

        Parameter
        ---------
        user : geokey.users.models.User
            User authenticated with the request
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base
        file_id : int
            identifies the file in the database

        Returns
        -------
        geokey.contributions.models.MediaFile
        """
        contribution = self.get_object(
            user,
            project_id,
            grouping_id,
            contribution_id
        )
        return contribution.files_attached.get(pk=file_id)

    @handle_exceptions_for_ajax
    def get(self, request, project_id, grouping_id, contribution_id, file_id,
            format=None):
        """
        Returns a single media file

        Parameter
        ---------
        user : geokey.users.models.User
            User authenticated with the request
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base
        file_id : int
            identifies the file in the database

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised file
        """
        media_file = self.get_file(
            request.user,
            project_id,
            grouping_id,
            contribution_id,
            file_id
        )
        return self.get_and_respond(request.user, media_file)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, grouping_id, contribution_id,
               file_id):
        """
        Deletes a single media file

        Parameter
        ---------
        user : geokey.users.models.User
            User authenticated with the request
        project_id : int
            identifies the project in the data base
        observation_id : int
            identifies the observation in the data base
        file_id : int
            identifies the file in the database

        Returns
        -------
        rest_framework.response.Respone
            Empty repsonse indicating success
        """
        media_file = self.get_file(
            request.user,
            project_id,
            grouping_id,
            contribution_id,
            file_id
        )
        return self.delete_and_respond(request.user, media_file)
