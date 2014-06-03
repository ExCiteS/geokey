from rest_framework import serializers
from core.serializers import FieldSelectorSerializer
from dataviews.serializers import ViewSerializer
from dataviews.models import View
from observationtypes.serializer import ObservationTypeSerializer

from .models import Project


class ProjectSerializer(FieldSelectorSerializer):
    """
    Serializer for projects.
    """
    is_admin = serializers.SerializerMethodField('get_admin')
    is_involved = serializers.SerializerMethodField('get_involved')
    can_contribute = serializers.SerializerMethodField('get_contribute')
    views = serializers.SerializerMethodField('get_views')
    observationtypes = ObservationTypeSerializer(read_only=True, many=True)

    class Meta:
        model = Project
        depth = 1
        fields = ('id', 'name', 'description', 'isprivate', 'status',
                  'created_at', 'observationtypes', 'is_admin',
                  'can_contribute', 'is_involved', 'views')
        read_only_fields = ('id', 'name')

    def get_admin(self, project):
        """
        Method for SerializerMethodField `is_admin`
        """
        return project.is_admin(self.context.get('user'))

    def get_contribute(self, project):
        """
        Method for SerializerMethodField `can_admin`
        """
        return project.can_contribute(self.context.get('user'))

    def get_involved(self, project):
        """
        Method for SerializerMethodField `is_involved`
        """
        return project.is_involved(self.context.get('user'))

    def get_views(self, project):
        """
        Method for SerializerMethodField `views`
        """
        user = self.context.get('user')
        views = View.objects.get_list(user, project.id)
        view_serializer = ViewSerializer(
            views, many=True, fields=('id', 'name', 'description'))
        return view_serializer.data
