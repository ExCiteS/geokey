from core.serializers import FieldSelectorSerializer
from rest_framework import serializers

from contributions.serializers import ContributionSerializer

from .models import View


class ViewSerializer(FieldSelectorSerializer):
    """
    Serializer for Views.
    """
    contributions = serializers.SerializerMethodField('get_data')
    num_contributions = serializers.SerializerMethodField(
        'get_number_contributions')

    class Meta:
        model = View
        depth = 1
        fields = ('id', 'name', 'description', 'status',
                  'created_at', 'contributions', 'isprivate', 'status',
                  'num_contributions')
        read_only_fields = ('id', 'name', 'created_at')

    def get_data(self, obj):
        """
        Returns all serialized contributions accessable through the view.
        """
        user = self.context.get('user')

        if (obj.project.can_moderate(user)):
            data = obj.data.for_moderator()
        else:
            data = obj.data.for_viewer()

        serializer = ContributionSerializer(
            data,
            many=True,
            context={'project': obj.project, 'user': user}
        )
        return serializer.data

    def get_number_contributions(self, obj):
        """
        Returns the number of contributions accessable through the view.
        """
        user = self.context.get('user')
        if (obj.project.can_moderate(user)):
            return len(obj.data.for_moderator())
        else:
            return len(obj.data.for_viewer())
