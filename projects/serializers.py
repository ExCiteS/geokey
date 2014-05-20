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

    def to_native(self, project):
        native = super(ProjectSerializer, self).to_native(project)
        request = self.context.get('request')
        if request is not None:
            native['can_contribute'] = project.can_contribute(request.user)
            native['is_admin'] = project.is_admin(request.user)

            views = View.objects.get_list(request.user, project.id)
            view_serializer = ViewSerializer(views, many=True)
            native['views'] = view_serializer.data

        return native
