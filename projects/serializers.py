from rest_framework import serializers

from users.serializers import UserSerializer

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

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(UserGroupSerializer, self).__init__(*args, **kwargs)

        if fields:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for projects.
    """
    creator = UserSerializer(read_only=True)
    admins = UserGroupSerializer(read_only=True, fields=('id', 'name'))
    contributors = UserGroupSerializer(read_only=True, fields=('id', 'name'))

    class Meta:
        model = Project
        depth = 1
        fields = ('id', 'name', 'description', 'isprivate', 'status',
                  'everyonecontributes', 'creator', 'admins', 'contributors',
                  'created_at')
        read_only_fields = ('id', 'name')
