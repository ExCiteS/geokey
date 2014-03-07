from rest_framework import serializers

from .models import View


class ViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = View
        depth = 1
        fields = ('id', 'name', 'description', 'status')
        read_only_fields = ('id', 'name')


class ViewUpdateSerializer(ViewSerializer):
    description = serializers.CharField(required=False)
