from rest_framework import serializers

from .models import Project
from .base import STATUS


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        depth = 1
        fields = ('id', 'name', 'description', 'isprivate', 'status',
                  'everyonecontributes', 'creator')
        read_only_fields = ('id', 'name', 'creator')


class ProjectUpdateSerializer(ProjectSerializer):
    description = serializers.CharField(required=False)
    isprivate = serializers.BooleanField(required=False)
    status = serializers.ChoiceField(choices=STATUS, required=False)
    everyonecontributes = serializers.BooleanField(required=False)
