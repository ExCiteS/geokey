from core.serializers import FieldSelectorSerializer
from rest_framework import serializers

from contributions.serializers import ContributionSerializer

from .models import View


class ViewSerializer(FieldSelectorSerializer):
    """
    Serializer for Views.
    """
    observations = serializers.SerializerMethodField('get_data')
    num_observations = serializers.SerializerMethodField(
        'get_number_observations')

    class Meta:
        model = View
        depth = 1
        fields = ('id', 'name', 'description', 'status',
                  'created_at', 'observations', 'isprivate', 'status',
                  'num_observations')
        read_only_fields = ('id', 'name', 'created_at')

    def get_data(self, obj):
        """
        Returns all serialized observations accessable through the view.
        """
        serializer = ContributionSerializer(obj.data, many=True)
        return serializer.data

    def get_number_observations(self, obj):
        """
        Returns the number of observations accessable through the view.
        """
        return len(obj.data)
