from rest_framework import serializers

from .models import Project, UserGroup


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        depth = 1
        fields = ('id', 'name', 'description', 'isprivate', 'status',
                  'everyonecontributes', 'creator')
        read_only_fields = ('id', 'name', 'creator')


class ProjectUpdateSerializer(ProjectSerializer):
    def __init__(self, *args, **kwargs):
        super(ProjectSerializer, self).__init__(*args, **kwargs)
        self.fields['description'].required = False


class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        depth = 1
        fields = ('id', 'name', 'users')
