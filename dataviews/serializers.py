from rest_framework import serializers

from users.serializers import UserSerializer

from .models import View, ViewGroup


class ViewSerializer(serializers.ModelSerializer):
    """
    Serializer for Views.
    """

    class Meta:
        model = View
        depth = 1
        fields = ('id', 'name', 'description', 'status',
                  'created_at')
        read_only_fields = ('id', 'name', 'created_at')


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
