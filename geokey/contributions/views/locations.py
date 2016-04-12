"""Views for locations of contributions."""

from django.db.models import Q

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from geokey.core.decorators import handle_exceptions_for_ajax
from geokey.users.models import User

from ..models import Location
from ..serializers import LocationSerializer


class LocationAbstractAPIView(APIView):
    """Abstract class for locations."""

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


class LocationsAPIView(LocationAbstractAPIView):
    """Public API for all locations."""

    @handle_exceptions_for_ajax
    def get(self, request, project_id):
        """
        Handle GET request.

        Return a list of all locations of the project, that can be used for
        contributions.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        project_id : int
            Identifies the project in the database.

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialised locations.
        """
        query = request.GET.get('query')
        locations = Location.objects.get_list(
            self.get_user(request),
            project_id
        )

        if query:
            query = query.lower()
            locations = locations.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SingleLocationAPIView(LocationAbstractAPIView):
    """Public API for a single location."""

    @handle_exceptions_for_ajax
    def patch(self, request, project_id, location_id):
        """
        Handle GET request.

        Update the location.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        project_id : int
            Identifies the project in the database.
        location_id : int
            Identifies the location in the database.

        Returns
        -------
        rest_framework.response.Respone
            Contains the serialized location.
        """
        location = Location.objects.get_single(
            self.get_user(request),
            project_id,
            location_id
        )
        serializer = LocationSerializer(
            location,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
