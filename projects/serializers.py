import json
from django.db.models import Q

from rest_framework import serializers

from core.serializers import FieldSelectorSerializer
from datagroupings.serializers import GroupingSerializer
from datagroupings.models import Grouping
from categories.serializer import CategorySerializer
from contributions.models import Location

from .models import Project


class ProjectSerializer(FieldSelectorSerializer):
    """
    Serializer for projects.
    """
    data_groupings = serializers.SerializerMethodField(
        'get_data_groupings')
    num_contributions = serializers.SerializerMethodField(
        'get_number_contrbutions')
    num_locations = serializers.SerializerMethodField(
        'get_number_locations')

    categories = serializers.SerializerMethodField(
        'get_categories')
    contribution_info = serializers.SerializerMethodField(
        'get_contribution_info')
    user_info = serializers.SerializerMethodField(
        'get_user_info')
    geographic_extent = serializers.SerializerMethodField(
        'get_extent')

    class Meta:
        model = Project
        depth = 1
        fields = ('id', 'name', 'description', 'isprivate', 'status',
                  'created_at', 'categories', 'data_groupings',
                  'contribution_info', 'user_info', 'num_locations',
                  'geographic_extent')
        read_only_fields = ('id', 'name')

    def get_categories(self, project):
        serializer = CategorySerializer(
            project.categories.all().exclude(fields=None), many=True)
        return serializer.data

    def get_data_groupings(self, project):
        """
        Method for SerializerMethodField `maps`
        """
        user = self.context.get('user')
        maps = Grouping.objects.get_list(user, project.id)
        view_serializer = GroupingSerializer(
            maps, many=True,
            fields=('id', 'name', 'description', 'num_contributions',
                    'created_at', 'symbol', 'colour'),
            context={'user': user})
        return view_serializer.data

    def get_extent(self, project):
        """
        Returns the geographic extent of the project as geojson.
        """
        if project.geographic_extend is not None:
            return json.loads(project.geographic_extend.json)
        else:
            return None

    def get_number_locations(self, project):
        """
        Method for SerializerMethodField `num_locations`. Returns the number
        available for the project.
        """
        locations = Location.objects.filter(
            Q(private=False) |
            Q(private_for_project=project)).count()
        return locations

    def get_number_contrbutions(self, project):
        """
        Method for SerializerMethodField `num_observations`. Returns the
        overall number of observations contributed to the project.
        """
        return project.observations.exclude(
            status='draft').exclude(status='pending').count()

    def get_user_contributions(self, project):
        """
        Method for SerializerMethodField `user_contributions`. Returns the
        overall number of observations contributed to the project by the user
        signed with the request.
        """
        user = self.context.get('user')
        if not user.is_anonymous():
            return project.observations.filter(creator=user).count()
        else:
            return 0

    def get_contribution_info(self, project):
        """
        Method for SerializerMethodField `contribution_info`
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
            'total': self.get_number_contrbutions(project),
            'personal': personal,
            'pending_all': pending_all,
            'pending_personal': pending_personal,
            'drafts': drafts
        }

    def get_user_info(self, project):
        return {
            'is_admin': project.is_admin(self.context.get('user')),
            'can_contribute': project.can_contribute(self.context.get('user')),
            'is_involved': project.is_involved(self.context.get('user')),
            'can_moderate': project.can_moderate(self.context.get('user'))
        }
