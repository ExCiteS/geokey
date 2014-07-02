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
        serializer = ContributionSerializer(obj.data, many=True)
        return serializer.data

    def get_number_contributions(self, obj):
        """
        Returns the number of contributions accessable through the view.
        """
        return len(obj.data)
