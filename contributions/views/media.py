from django.core.exceptions import PermissionDenied

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from core.exceptions import MalformedRequestData
from core.decorators import handle_exceptions_for_ajax
from .base import (
    SingleAllContribution, SingleGroupingContribution, SingleMyContribution
)

from users.models import User
from ..serializers import FileSerializer
from ..models.media import MediaFile


class MediaFileListAbstractAPIView(APIView):
    def get_list_and_respond(self, user, contribution):
        """
        Serialises all files attached to the contribution and returns the
        JSON response
        """
        files = contribution.files_attached.all()
        serializer = FileSerializer(
            files, many=True, context={'user': user})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create_and_respond(self, user, contribution):
        """
        Creates an image and responds with the file information
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

    @handle_exceptions_for_ajax
    def get(self, request, project_id, contribution_id, format=None):
        """
        Returns a list of all files attached to the observation
        """
        contribution = self.get_object(
            request.user,
            project_id,
            contribution_id
        )
        return self.get_list_and_respond(request.user, contribution)

    @handle_exceptions_for_ajax
    def post(self, request, project_id, contribution_id, format=None):
        contribution = self.get_object(
            request.user,
            project_id,
            contribution_id
        )
        return self.create_and_respond(request.user, contribution)


class MyContributionsMediaApiView(
        MediaFileListAbstractAPIView, SingleMyContribution):

    @handle_exceptions_for_ajax
    def get(self, request, project_id, contribution_id, format=None):
        """
        Returns a list of all files attached to the observation
        """
        contribution = self.get_object(
            request.user,
            project_id,
            contribution_id
        )
        return self.get_list_and_respond(request.user, contribution)

    @handle_exceptions_for_ajax
    def post(self, request, project_id, contribution_id, format=None):
        contribution = self.get_object(
            request.user,
            project_id,
            contribution_id
        )
        return self.create_and_respond(request.user, contribution)


class GroupingContributionsMediaApiView(
        MediaFileListAbstractAPIView, SingleGroupingContribution):

    @handle_exceptions_for_ajax
    def get(self, request, project_id, grouping_id, contribution_id,
            format=None):
        """
        Returns a list of all files attached to the observation
        """
        contribution = self.get_object(
            request.user,
            project_id,
            grouping_id,
            contribution_id
        )
        return self.get_list_and_respond(request.user, contribution)

    @handle_exceptions_for_ajax
    def post(self, request, project_id, grouping_id, contribution_id,
             format=None):
        contribution = self.get_object(
            request.user,
            project_id,
            grouping_id,
            contribution_id
        )
        return self.create_and_respond(request.user, contribution)


class MediaFileSingleAbstractView(APIView):
    def get_and_respond(self, user, media_file):
        serializer = FileSerializer(media_file, context={'user': user})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete_and_respond(self, user, media_file):
        if (media_file.creator == user or
                media_file.contribution.project.can_moderate(user)):
            media_file.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        raise PermissionDenied('You neither are the creator if this file '
                               'nor a project moderator and therefore '
                               'not eligable to delete this file.')


class AllContributionsSingleMediaApiView(
        MediaFileSingleAbstractView, SingleAllContribution):

    def get_file(self, user, project_id, contribution_id, file_id):
        contribution = self.get_object(user, project_id, contribution_id)
        return contribution.files_attached.get(pk=file_id)

    @handle_exceptions_for_ajax
    def get(self, request, project_id, contribution_id, file_id, format=None):
        media_file = self.get_file(
            request.user,
            project_id,
            contribution_id,
            file_id
        )
        return self.get_and_respond(request.user, media_file)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, contribution_id, file_id,
               format=None):
        media_file = self.get_file(
            request.user,
            project_id,
            contribution_id,
            file_id
        )
        return self.delete_and_respond(request.user, media_file)


class MyContributionsSingleMediaApiView(
        MediaFileSingleAbstractView, SingleMyContribution):

    def get_file(self, user, project_id, contribution_id, file_id):
        contribution = self.get_object(user, project_id, contribution_id)
        return contribution.files_attached.get(pk=file_id)

    @handle_exceptions_for_ajax
    def get(self, request, project_id, contribution_id, file_id, format=None):
        media_file = self.get_file(
            request.user,
            project_id,
            contribution_id,
            file_id
        )
        return self.get_and_respond(request.user, media_file)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, contribution_id, file_id,
               format=None):
        media_file = self.get_file(
            request.user,
            project_id,
            contribution_id,
            file_id
        )
        return self.delete_and_respond(request.user, media_file)


class GroupingContributionsSingleMediaApiView(
        MediaFileSingleAbstractView, SingleGroupingContribution):

    def get_file(self, user, project_id, grouping_id, contribution_id,
                 file_id):
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
               file_id, format=None):
        media_file = self.get_file(
            request.user,
            project_id,
            grouping_id,
            contribution_id,
            file_id
        )
        return self.delete_and_respond(request.user, media_file)
