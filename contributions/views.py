from django.core.exceptions import PermissionDenied
from django.db.models import Q

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from core.decorators import handle_exceptions_for_ajax
from core.exceptions import MalformedRequestData

from .serializers import (
    ContributionSerializer, LocationSerializer, CommentSerializer,
    FileSerializer
)
from .models import Location, Comment, Observation, ImageFile
from projects.models import Project
from dataviews.models import View
from dataviews.serializers import ViewSerializer
from users.models import User


# ############################################################################
#
# Locations
#
# ############################################################################

class Locations(APIView):
    """
    Public API endpoint for all locations in a project.
    /api/projects/:project_id/locations/
    """

    @handle_exceptions_for_ajax
    def get(self, request, project_id, format=None):
        """
        Returns a list of locations that can be used for contributions to the
        given project.
        """
        q = request.GET.get('query')
        locations = Location.objects.get_list(request.user, project_id)

        if q is not None:
            locations = locations.filter(Q(name__icontains=q.lower()) |
                Q(description__icontains=q.lower()))

        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)


class SingleLocation(APIView):
    """
    Public API endpoint for a single location in a project.
    /api/projects/:project_id/locations/:location_id/
    """
    @handle_exceptions_for_ajax
    def patch(self, request, project_id, location_id, format=None):
        location = Location.objects.get_single(
            request.user, project_id, location_id)
        serializer = LocationSerializer(
            location, data=request.DATA, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ############################################################################
#
# Observations
#
# ############################################################################

class ProjectObservations(APIView):
    """
    Public API endpoint to add new contributions to a project
    /api/projects/:project_id/contributions
    """
    @handle_exceptions_for_ajax
    def post(self, request, project_id, format=None):
        """
        Adds a new contribution to a project
        """
        user = request.user
        if user.is_anonymous():
            user = User.objects.get(display_name='AnonymousUser')

        data = request.DATA
        project = Project.objects.as_contributor(request.user, project_id)

        if (not data.get('properties').get('status') == 'draft' and
                project.can_moderate(user)):
            data['properties']['status'] = 'active'

        serializer = ContributionSerializer(
            data=data, context={'user': user, 'project': project}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ContributionSearchAPIView(APIView):
    """
    Public API endpoint to search all contributions in a project
    /api/projects/:project_id/contributions/search/?query={query}
    """
    @handle_exceptions_for_ajax
    def get(self, request, project_id, format=None):
        q = request.GET.get('query')

        project = Project.objects.get_single(request.user, project_id)
        contributions = project.get_all_contributions(
            request.user).filter(attributes__icontains=q)

        serializer = ContributionSerializer(
            contributions,
            many=True,
            context={'user': request.user, 'project': project}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)



class ProjectObservationsView(APIView):
    """
    Public API endpoint to get all contributions in a project
    /api/projects/:project_id/data-groupings/all-contributions/
    """
    @handle_exceptions_for_ajax
    def get(self, request, project_id, format=None):
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
    Public API endpoint for all observations in a project. Used to add new
    contributions to a project
    /api/projects/:project_id/data-groupings/my-contributions/
    """

    @handle_exceptions_for_ajax
    def get(self, request, project_id, format=None):
        project = Project.objects.get_single(request.user, project_id)
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
    @handle_exceptions_for_ajax
    def get(self, request, project_id, view_id, format=None):
        """
        Returns a single view and its data
        /api/projects/:project_id/data-groupings/:view_id/
        """
        view = View.objects.get_single(request.user, project_id, view_id)
        serializer = ViewSerializer(view, context={'user': request.user})
        return Response(serializer.data)


# ############################################################################
# 
# SINGLE CONTRIBUTIONS
# 
# ############################################################################


class SingleContributionAPIView(APIView):
    def get_and_respond(self, request, observation, format=None):
        serializer = ContributionSerializer(
            observation,
            context={'user': request.user, 'project': observation.project}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update_and_respond(self, request, observation, format=None):
        data = request.DATA
        user = request.user
        if user.is_anonymous():
            user = User.objects.get(display_name='AnonymousUser')

        new_status = data.get('properties').get('status')

        if (new_status is not None and new_status != observation.status):
            if new_status == 'pending':
                data = {
                    'properties': {
                        'status': new_status,
                        'review_comment': data.get('properties').get('review_comment')
                    }
                }
            elif not ((new_status == 'active' and observation.status == 'draft' and
                observation.creator == user) or (new_status == 'active' and
                    observation.status == 'pending' and
                    observation.project.can_moderate(user))):
                raise PermissionDenied('You are not allowed to update the status '
                                       'of the observation to "%s"' % new_status)

        elif not (user == observation.creator or
                observation.project.can_moderate(user)):
            raise PermissionDenied('You are not allowed to update the'
                                   'contribution')

        if ((new_status == 'active' and observation.status == 'draft') and
                not observation.project.can_moderate(user)):
            data['properties']['status'] = observation.observationtype.default_status

        serializer = ContributionSerializer(
            observation,
            data=data,
            context={'user': user, 'project': observation.project}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete_and_respond(self, request, observation, format=None):
        """
        Deletes a single observation
        """
        if (observation.creator == request.user or
                observation.project.can_moderate(request.user)):
            observation.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        raise PermissionDenied('You are not allowed to delete this'
                               'contribution')


class SingleAllContribution(object):
    def get_object(self, user, project_id, observation_id):
        project = Project.objects.get_single(user, project_id)

        if project.can_moderate(user):
            return project.get_all_contributions(
                user).for_moderator(user).get(pk=observation_id)
        else:
            return project.get_all_contributions(
                user).for_viewer(user).get(pk=observation_id)

class SingleGroupingContribution(object):
    def get_object(self, user, project_id, view_id, observation_id):
        view = View.objects.get_single(user, project_id, view_id)

        if view.project.can_moderate(user):
            return view.data.for_moderator(user).get(pk=observation_id)
        else:
            return view.data.for_viewer(user).get(pk=observation_id)

class SingleMyContribution(object):
    def get_object(self, user, project_id, observation_id):
        observation = Project.objects.get_single(
            user, project_id).observations.get(pk=observation_id)

        if observation.creator == user:
            return observation
        else:
            raise Observation.DoesNotExist('You are not the creator of this '
                                           'contribution or the contribution '
                                           'has been deleted.')


class SingleAllContributionAPIView(
    SingleAllContribution, SingleContributionAPIView):
    """
    Public API endpoint for updating a single observation in a project
    /api/projects/:project_id/observations/:observation_id
    """

    @handle_exceptions_for_ajax
    def get(self, request, project_id, observation_id, format=None):
        observation = self.get_object(request.user, project_id, observation_id)
        return self.get_and_respond(request, observation, format=format)

    @handle_exceptions_for_ajax
    def patch(self, request, project_id, observation_id, format=None):
        observation = self.get_object(request.user, project_id, observation_id)
        return self.update_and_respond(request, observation, format=format)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, observation_id, format=None):
        observation = self.get_object(request.user, project_id, observation_id)
        return self.delete_and_respond(request, observation, format=format)

        raise PermissionDenied('You are not eligable to delete this '
                               'contribution')


class SingleGroupingContributionAPIView(
    SingleGroupingContribution, SingleContributionAPIView):
    """
    Public API endpoint for updating a single observation in a project
    /api/projects/:project_id/views/:view_id/observations/:observation_id
    """
    @handle_exceptions_for_ajax
    def get(self, request, project_id, view_id, observation_id, format=None):
        observation = self.get_object(
            request.user, project_id, view_id, observation_id)
        return self.get_and_respond(request, observation, format=format)

    @handle_exceptions_for_ajax
    def patch(self, request, project_id, view_id, observation_id, format=None):
        observation = self.get_object(
            request.user, project_id, view_id, observation_id)
        return self.update_and_respond(request, observation, format=format)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, view_id, observation_id,
               format=None):
        observation = self.get_object(
            request.user, project_id, view_id, observation_id)
        return self.delete_and_respond(request, observation, format=format)


class SingleMyContributionAPIView(
    SingleMyContribution, SingleContributionAPIView):

    @handle_exceptions_for_ajax
    def get(self, request, project_id, observation_id, format=None):
        observation = self.get_object(request.user, project_id, observation_id)
        return self.get_and_respond(request, observation, format=format)

    @handle_exceptions_for_ajax
    def patch(self, request, project_id, observation_id, format=None):
        observation = self.get_object(request.user, project_id, observation_id)
        return self.update_and_respond(request, observation, format=format)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, observation_id, format=None):
        observation = self.get_object(request.user, project_id, observation_id)
        return self.delete_and_respond(request, observation, format=format)


# ############################################################################
#
# Comments
#
# ############################################################################

class CommentAbstractAPIView(APIView):
    def get_list_and_respond(self, user, observation):
        comments = observation.comments.filter(respondsto=None)
        serializer = CommentSerializer(
            comments, many=True, context={'user': user})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create_and_respond(self, request, observation):
        user = request.user
        if user.is_anonymous():
            user = User.objects.get(display_name='AnonymousUser')

        respondsto = None
        if request.DATA.get('respondsto') is not None:
            try:
                respondsto = observation.comments.get(
                    pk=request.DATA.get('respondsto'))
            except Comment.DoesNotExist:
                raise MalformedRequestData('The comment you try to respond to'
                                           ' is not a comment to the '
                                           'observation.')

        comment = Comment.objects.create(
            text=request.DATA.get('text'),
            respondsto=respondsto,
            commentto=observation,
            creator=user
        )

        serializer = CommentSerializer(comment, context={'user': user})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_and_respond(self, request, comment):
        if (comment.creator == request.user or
                comment.commentto.project.is_admin(request.user)):
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied('You are neither the author if this comment'
                                   ' nor a project administrator and therefore'
                                   ' not eligable to delete this comment.')


class AllContributionsCommentsAPIView(
        CommentAbstractAPIView, SingleAllContribution):

    @handle_exceptions_for_ajax
    def get(self, request, project_id, observation_id, format=None):
        """
        Returns a list of all comments of the observation
        """
        observation = self.get_object(request.user, project_id, observation_id)
        return self.get_list_and_respond(request.user, observation)

    @handle_exceptions_for_ajax
    def post(self, request, project_id, observation_id, format=None):
        """
        Adds a new comment to the observation
        """
        observation = self.get_object(request.user, project_id, observation_id)
        return self.create_and_respond(request, observation)


class AllContributionsSingleCommentAPIView(
        CommentAbstractAPIView, SingleAllContribution):

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, observation_id, comment_id,
               format=None):
        observation = self.get_object(request.user, project_id, observation_id)
        comment = observation.comments.get(pk=comment_id)
        return self.delete_and_respond(request, comment)


class GroupingContributionsCommentsAPIView(
        CommentAbstractAPIView, SingleGroupingContribution):

    @handle_exceptions_for_ajax
    def get(self, request, project_id, view_id, observation_id, format=None):
        """
        Returns a list of all comments of the observation
        """
        observation = self.get_object(
            request.user, project_id, view_id, observation_id)
        return self.get_list_and_respond(request.user, observation)

    @handle_exceptions_for_ajax
    def post(self, request, project_id, view_id, observation_id, format=None):
        """
        Adds a new comment to the observation
        """
        observation = self.get_object(
            request.user, project_id, view_id, observation_id)
        return self.create_and_respond(request, observation)


class GroupingContributionsSingleCommentAPIView(
        CommentAbstractAPIView, SingleGroupingContribution):

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, view_id, observation_id, comment_id,
               format=None):
        observation = self.get_object(
            request.user, project_id, view_id, observation_id)
        comment = observation.comments.get(pk=comment_id)
        return self.delete_and_respond(request, comment)


class MyContributionsCommentsAPIView(
    CommentAbstractAPIView, SingleMyContribution):

    @handle_exceptions_for_ajax
    def get(self, request, project_id, observation_id, format=None):
        observation = self.get_object(request.user, project_id, observation_id)
        return self.get_list_and_respond(request.user, observation)

    @handle_exceptions_for_ajax
    def post(self, request, project_id, observation_id, format=None):
        """
        Adds a new comment to the observation
        """
        observation = self.get_object(request.user, project_id, observation_id)
        return self.create_and_respond(request, observation)


class MyContributionsSingleCommentAPIView(
    CommentAbstractAPIView, SingleMyContribution):

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, observation_id, comment_id,
               format=None):
        observation = self.get_object(request.user, project_id, observation_id)
        comment = observation.comments.get(pk=comment_id)
        return self.delete_and_respond(request, comment)


# ############################################################################
#
# Media
#
# ############################################################################

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
        user = self.request.user
        data = self.request.POST

        if user.is_anonymous():
            user = User.objects.get(display_name='AnonymousUser')

        image = ImageFile.objects.create(
            name=data.get('name'),
            description=data.get('description'),
            contribution=contribution,
            creator=user,
            image=self.request.FILES.get('file')
        )
        serializer = FileSerializer(image, context={'user': user})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
