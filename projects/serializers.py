from core.serializers import FieldSelectorSerializer
from dataviews.serializers import ViewSerializer
from dataviews.models import View
from observationtypes.serializer import ObservationTypeSerializer

from .models import Project


class ProjectSerializer(FieldSelectorSerializer):
    """
    Serializer for projects.
    """
    observationtypes = ObservationTypeSerializer(read_only=True, many=True)

    class Meta:
        model = Project
        depth = 1
        fields = ('id', 'name', 'description', 'isprivate', 'status',
                  'created_at', 'observationtypes')
        read_only_fields = ('id', 'name')
        write_only_fields = ('status',)

    def to_native(self, project):
        """
        Overides `to_native` of `rest_framework.serializers.ModelSerializer`.
        If the request context is set, the methods adds additional user
        specific fields to the serialized project, e.g. if the user is admin,
        can contribute, is involved in projects and all views the user can
        access.
        """
        native = super(ProjectSerializer, self).to_native(project)
        request = self.context.get('request')
        if request is not None:
            native['can_contribute'] = project.can_contribute(request.user)
            native['is_admin'] = project.is_admin(request.user)
            native['is_involved'] = project.is_involved(request.user)

            views = View.objects.get_list(request.user, project.id)
            view_serializer = ViewSerializer(
                views, many=True, fields=('id', 'name', 'description'))
            native['views'] = view_serializer.data

        return native
