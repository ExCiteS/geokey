from rest_framework import serializers

from users.serializers import UserSerializer
from contributions.serializers import ContributionSerializer

from .models import View, ViewGroup


class ViewSerializer(serializers.ModelSerializer):
    """
    Serializer for Views.
    """
    observations = serializers.SerializerMethodField('get_data')

    class Meta:
        model = View
        depth = 1
        fields = ('id', 'name', 'description', 'status',
                  'created_at', 'observations')
        read_only_fields = ('id', 'name', 'created_at')

    def get_data(self, obj):
        serializer = ContributionSerializer(obj.data, many=True)
        return serializer.data


class ViewGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for ViewGroups.
    """
    users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = ViewGroup
        depth = 1
        fields = (
            'id', 'name', 'description', 'status', 'can_view', 'can_read',
            'can_edit', 'users'
        )
        read_only_fields = ('id', 'name', 'status')
