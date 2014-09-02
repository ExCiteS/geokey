from django.db.models import Q

from rest_framework import serializers

from core.serializers import FieldSelectorSerializer
from dataviews.serializers import ViewSerializer
from dataviews.models import View
from observationtypes.serializer import ObservationTypeSerializer
from contributions.models import Location

from .models import Project


class ProjectSerializer(FieldSelectorSerializer):
    """
    Serializer for projects.
    """
    maps = serializers.SerializerMethodField('get_maps')
    num_maps = serializers.SerializerMethodField('get_number_maps')
    num_contributions = serializers.SerializerMethodField(
        'get_number_contrbutions')
    num_locations = serializers.SerializerMethodField(
        'get_number_locations')
    user_contributions = serializers.SerializerMethodField(
        'get_user_contributions')
    contributiontypes = serializers.SerializerMethodField(
        'get_contributiontypes')

    can_access_all_contributions = serializers.SerializerMethodField(
        'get_can_access_all_map')
    can_contribute = serializers.SerializerMethodField('get_contribute')
    can_moderate = serializers.SerializerMethodField('get_moderate')
    is_admin = serializers.SerializerMethodField('get_admin')
    is_involved = serializers.SerializerMethodField('get_involved')

    class Meta:
        model = Project
        depth = 1
        fields = ('id', 'name', 'description', 'isprivate',
                  'everyone_contributes', 'status',
                  'created_at', 'contributiontypes', 'maps', 'num_maps',
                  'num_contributions', 'num_locations', 'user_contributions',
                  'is_admin', 'can_contribute', 'is_involved', 'can_moderate')
        read_only_fields = ('id', 'name')

    def get_contributiontypes(self, project):
        serializer = ObservationTypeSerializer(
            project.observationtypes.active().exclude(fields=None), many=True)
        return serializer.data

    def get_admin(self, project):
        """
        Method for SerializerMethodField `is_admin`
        """
        return project.is_admin(self.context.get('user'))

    def get_can_access_all_map(self, project):
        """
        Method for SerializerMethodField `can_access_all_contributions`
        """
        return project.can_access_all_contributions(self.context.get('user'))

    def get_contribute(self, project):
        """
        Method for SerializerMethodField `can_contribute`
        """
        return project.can_contribute(self.context.get('user'))

    def get_moderate(self, project):
        """
        Method for SerializerMethodField `can_moderate`
        """
        return project.can_moderate(self.context.get('user'))

    def get_involved(self, project):
        """
        Method for SerializerMethodField `is_involved`
        """
        return project.is_involved(self.context.get('user'))

    def get_maps(self, project):
        """
        Method for SerializerMethodField `maps`
        """
        user = self.context.get('user')
        maps = View.objects.get_list(user, project.id)
        view_serializer = ViewSerializer(
            maps, many=True,
            fields=('id', 'name', 'description', 'num_contributions'),
            context={'user': user})
        return view_serializer.data

    def get_number_maps(self, project):
        """
        Method for SerializerMethodField `num_maps`. Returns the number of
        maps the user is allowed to access.
        """
        user = self.context.get('user')
        return View.objects.get_list(user, project.id).count()

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
        if project.can_moderate(self.context.get('user')):
            return project.observations.exclude(status='draft').count()

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
