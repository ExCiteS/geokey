"""Views for media files of contributions."""

from django.core.exceptions import PermissionDenied

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from geokey.core.decorators import handle_exceptions_for_ajax
from geokey.core.exceptions import MalformedRequestData
from geokey.users.models import User

from .base import SingleAllContribution
from ..models import MediaFile
from ..serializers import FileSerializer


class MediaAbstractAPIView(APIView):
    """Abstract class for media."""

    def get_user(self, request):
        """
        Get user of a request.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.

        Returns
        -------
        geokey.users.models.User
            User of a request.
        """
        user = request.user

        if user.is_anonymous():
            user = User.objects.get(display_name='AnonymousUser')

        return user

    def get_file(self, contribution, file_id):
        """
        Get media file of a contribution.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        contribution : geokey.contributions.models.Observation
            Contribution to retrieve the file from.
        file_id : int
            Identifies the media file in the database.

        Returns
        -------
        geokey.contributions.models.MediaFile
            Media file of a contribution.
        """
        return contribution.files_attached\
            .select_related('creator')\
            .get(pk=file_id)

    def get_list_and_respond(self, request, contribution):
        """
        Respond to a GET request with a list of all media files.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        contribution : geokey.contributions.models.Observation
            Contribution the media files are requested for.

        Returns
        -------
        rest_framework.response.Respones
            Contains the serialized media files.
        """
        serializer = FileSerializer(
            contribution.files_attached.all(),
            many=True,
            context={'user': self.get_user(request)}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create_and_respond(self, request, contribution):
        """
        Respond to a POST request by creating a media file.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        contribution : geokey.contributions.models.Observation
            Contribution the media file should be added to.

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialized media file.

        Raises
        ------
        MalformedRequestData
            When name is not set or file is not attached.
        PermissionDenied
            When user is not allowed to contribute to the project.
        """
        user = self.get_user(request)

        data = self.request.POST
        name = data.get('name')
        description = data.get('description')
        file = self.request.FILES.get('file')

        errors = []
        if name is None:
            errors.append('Property `name` is not set')
        if file is None:
            errors.append('No file attached')
        if errors:
            raise MalformedRequestData('%s.' % ', '.join(errors))

        if contribution.project.can_contribute(user):
            file = MediaFile.objects.create(
                name=name,
                description=description,
                contribution=contribution,
                creator=user,
                the_file=file
            )

            serializer = FileSerializer(file, context={'user': user})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise PermissionDenied(
                'You are not allowed to contribute to the project.'
            )

    def get_single_and_respond(self, request, file):
        """
        Respond to a GET request with a single media file.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        file : geokey.contributions.models.MediaFile
            Media file to be returned.

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialized media file.
        """
        serializer = FileSerializer(
            file,
            context={'user': self.get_user(request)}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete_and_respond(self, request, contribution, file):
        """
        Respond to a DELETE request by deleting the media file.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        contribution : geokey.contributions.models.Observation
            Contribution of a media file.
        file : geokey.contributions.models.MediaFile
            Media file to be deleted.

        Returns
        -------
        rest_framework.response.Respone
            Empty response indicating success.

        Raises
        ------
        PermissionDenied
            When user is not allowed to delete the media file.
        """
        user = self.get_user(request)

        if file.creator == user or contribution.project.can_moderate(user):
            file.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied(
                'You are neither the creator if this file nor a project '
                'moderator and therefore not eligable to delete it.'
            )


class MediaAPIView(SingleAllContribution, MediaAbstractAPIView):
    """Public API for all media files."""

    @handle_exceptions_for_ajax
    def get(self, request, project_id, contribution_id):
        """
        Handle GET request.

        Return a list of all media files of the contribution.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        project_id : int
            Identifies the project in the database.
        contribution_id : int
            Identifies the contribution in the database.

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised media files.
        """
        contribution = self.get_contribution(
            request.user,
            project_id,
            contribution_id
        )

        return self.get_list_and_respond(request, contribution)

    @handle_exceptions_for_ajax
    def post(self, request, project_id, contribution_id):
        """
        Handle POST request.

        Add a new media file to the contribution.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        project_id : int
            Identifies the project in the database.
        contribution_id : int
            Identifies the contribution in the database.

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised media file.
        """
        contribution = self.get_contribution(
            request.user,
            project_id,
            contribution_id
        )

        return self.create_and_respond(request, contribution)


class SingleMediaAPIView(SingleAllContribution, MediaAbstractAPIView):
    """Public API for a single media."""

    @handle_exceptions_for_ajax
    def get(self, request, project_id, contribution_id, file_id):
        """
        Handle GET request.

        Return a single media file.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        project_id : int
            Identifies the project in the database.
        contribution_id : int
            Identifies the contribution in the database.
        file_id : int
            Identifies the media file in the database.

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialized media file.
        """
        contribution = self.get_contribution(
            request.user,
            project_id,
            contribution_id
        )
        file = self.get_file(contribution, file_id)

        return self.get_single_and_respond(request, file)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, contribution_id, file_id):
        """
        Handle DELETE request.

        Delete the media file.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        project_id : int
            Identifies the project in the database.
        contribution_id : int
            Identifies the contribution in the database.
        file_id : int
            Identifies the media file in the database.

        Returns
        -------
        rest_framework.response.Respone
            Empty response indicating success.
        """
        contribution = self.get_contribution(
            request.user,
            project_id,
            contribution_id
        )
        file = self.get_file(contribution, file_id)

        return self.delete_and_respond(request, contribution, file)
