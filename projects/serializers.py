from rest_framework import serializers

from core.serializers import FieldSelectorSerializer
from users.serializers import UserSerializer
from dataviews.serializers import ViewSerializer
from dataviews.models import View
from observationtypes.serializer import ObservationTypeSerializer

from .models import Project, UserGroup


class UserGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for project user groups.
    """
    users = UserSerializer(many=True)

    class Meta:
        model = UserGroup
        depth = 1
        fields = ('id', 'name', 'users')


class ProjectSerializer(FieldSelectorSerializer):
    """
    Serializer for projects.
    """
    observationtypes = ObservationTypeSerializer(read_only=True, many=True)

    class Meta:
        model = Project
        depth = 1
        fields = ('id', 'name', 'description', 'isprivate', 'status',
                  'everyonecontributes', 'created_at',
                  'observationtypes')
        read_only_fields = ('id', 'name')
        write_only_fields = ('isprivate', 'everyonecontributes')

    def to_native(self, project):
        native = super(ProjectSerializer, self).to_native(project)
        request = self.context.get('request')
        if request is not None:
            native['can_contribute'] = project.can_contribute(request.user)

            views = View.objects.get_list(request.user, project.id)
            view_serializer = ViewSerializer(views, many=True)
            native['views'] = view_serializer.data

        return native
