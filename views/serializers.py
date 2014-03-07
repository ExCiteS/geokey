from rest_framework import serializers

from users.serializers import UserSerializer

from .models import View, ViewGroup


class ViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = View
        depth = 1
        fields = ('id', 'name', 'description', 'status')
        read_only_fields = ('id', 'name')


class ViewUpdateSerializer(ViewSerializer):
    description = serializers.CharField(required=False)


class ViewGroupSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = ViewGroup
        depth = 1
        fields = (
            'id', 'name', 'description', 'status', 'can_view', 'can_read',
            'can_edit', 'users'
        )
        read_only_fields = ('id', 'name', 'status')


class ViewGroupUpdateSerializer(ViewGroupSerializer):
    description = serializers.CharField(required=False)
