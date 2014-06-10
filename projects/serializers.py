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
    num_views = serializers.SerializerMethodField('get_number_views')
    num_observations = serializers.SerializerMethodField(
        'get_number_observations')
    user_contributions = serializers.SerializerMethodField(
        'get_user_contributions')
    observationtypes = ObservationTypeSerializer(read_only=True, many=True)

    class Meta:
        model = Project
        depth = 1
        fields = ('id', 'name', 'description', 'isprivate', 'status',
                  'created_at', 'observationtypes', 'is_admin',
                  'can_contribute', 'is_involved', 'views', 'num_views',
                  'num_observations', 'user_contributions')
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
            views, many=True,
            fields=('id', 'name', 'description', 'num_observations'))
        return view_serializer.data

    def get_number_views(self, project):
        """
        Method for SerializerMethodField `num_views`. Returns the number of
        views the user is allowed to access.
        """
        user = self.context.get('user')
        return View.objects.get_list(user, project.id).count()

    def get_number_observations(self, project):
        """
        Method for SerializerMethodField `num_observations`. Returns the overall
        number of observations contributed to the project.
        """
        return project.observations.count()

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
