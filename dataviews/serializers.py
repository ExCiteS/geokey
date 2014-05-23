from core.serializers import FieldSelectorSerializer
from rest_framework import serializers

from contributions.serializers import ContributionSerializer

from .models import View


class ViewSerializer(FieldSelectorSerializer):
    """
    Serializer for Views.
    """
    observations = serializers.SerializerMethodField('get_data')

    class Meta:
        model = View
        depth = 1
        fields = ('id', 'name', 'description', 'status',
                  'created_at', 'observations', 'ispublic')
        read_only_fields = ('id', 'name', 'created_at')

    def get_data(self, obj):
        serializer = ContributionSerializer(obj.data, many=True)
        return serializer.data
