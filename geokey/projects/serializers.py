"""Serializers for projects."""

import json

from django.db.models import Q

from rest_framework import serializers

from geokey.core.serializers import FieldSelectorSerializer
from geokey.categories.serializers import CategorySerializer
from geokey.subsets.serializers import SubsetSerializer
from geokey.contributions.models import Location

from .models import Project


class ProjectSerializer(FieldSelectorSerializer):
    """
    Serializer for geokey.projects.models.Project
    """
    num_locations = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    contribution_info = serializers.SerializerMethodField()
    user_info = serializers.SerializerMethodField()
    geographic_extent = serializers.SerializerMethodField()
    subsets = serializers.SerializerMethodField()

    class Meta:
        model = Project
        depth = 1
        fields = ('id', 'name', 'description', 'isprivate', 'islocked',
                  'status', 'created_at', 'categories', 'subsets',
                  'contribution_info', 'user_info', 'num_locations',
                  'geographic_extent')
        read_only_fields = ('id', 'name')

    def get_subsets(self, project):
        """
        Returns all serialised subset of the project

        Parameters
        ----------
        project : geokey.projects.models.Project
            Project that is serialised

        Returns
        -------
        list
            serialised subsets
        """
        serializer = SubsetSerializer(project.subsets.all(), many=True)
        return serializer.data

    def get_categories(self, project):
        """
        Returns all serialised categories of the project

        Parameters
        ----------
        project : geokey.projects.models.Project
            Project that is serialised

        Returns
        -------
        list
            serialised categories
        """
        serializer = CategorySerializer(
            project.categories.all().exclude(fields=None), many=True)
        return serializer.data

    def get_geographic_extent(self, project):
        """
        Returns the geographic extent of the project as geojson.

        Parameters
        ----------
        project : geokey.projects.models.Project
            Project that is serialised

        Returns
        -------
        dict
            serialised geometry of the extent
        """
        if project.geographic_extent is not None:
            return json.loads(project.geographic_extent.json)
        else:
            return None

    def get_num_locations(self, project):
        """
        Method for SerializerMethodField `num_locations`. Returns the number
        available for the project.

        Parameters
        ----------
        project : geokey.projects.models.Project
            Project that is serialised

        Returns
        -------
        int
            number of locations in the project
        """
        locations = Location.objects.filter(
            Q(private=False) |
            Q(private_for_project=project)).count()
        return locations

    def get_num_contributions(self, project):
        """
        Method for SerializerMethodField `num_observations`. Returns the
        overall number of observations contributed to the project.

        Parameters
        ----------
        project : geokey.projects.models.Project
            Project that is serialised

        Returns
        -------
        int
            number of contributions in the project
        """
        return project.observations.exclude(
            status='draft').exclude(status='pending').count()

    def get_user_contributions(self, project):
        """
        Method for SerializerMethodField `user_contributions`. Returns the
        overall number of observations contributed to the project by the user
        signed with the request.

        Parameters
        ----------
        project : geokey.projects.models.Project
            Project that is serialised

        Returns
        -------
        int
            number of user's contributions in the project
        """
        user = self.context.get('user')
        if not user.is_anonymous():
            return project.observations.filter(creator=user).count()
        else:
            return 0

    def get_contribution_info(self, project):
        """
        Method for SerializerMethodField `contribution_info`. Returns numbers
        on user's contributions.

        Parameters
        ----------
        project : geokey.projects.models.Project
            Project that is serialised

        Returns
        -------
        dict
            numbers of user's contributions in the project
        """
        drafts = 0
        pending_personal = 0
        personal = 0
        pending_all = None

        user = self.context.get('user')
        if not user.is_anonymous():
            personal = project.observations.filter(creator=user).count()
            pending_personal = project.observations.filter(
                creator=user, status='pending').count()
            drafts = project.observations.filter(
                creator=user, status='draft').count()

            if project.can_moderate(user):
                pending_all = project.observations.filter(
                    status='pending').count()

        return {
            'total': self.get_num_contributions(project),
            'personal': personal,
            'pending_all': pending_all,
            'pending_personal': pending_personal,
            'drafts': drafts
        }

    def get_user_info(self, project):
        """
        Returns the roles of the user in the project

        Parameters
        ----------
        project : geokey.projects.models.Project
            Project that is serialised

        Returns
        -------
        dict
            user roles in the project
        """
        return {
            'is_admin': project.is_admin(self.context.get('user')),
            'can_contribute': project.can_contribute(self.context.get('user')),
            'is_involved': project.is_involved(self.context.get('user')),
            'can_moderate': project.can_moderate(self.context.get('user'))
        }
