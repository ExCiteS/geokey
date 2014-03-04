from rest_framework import serializers

from .models import ObservationType


class ObservationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservationType
        depth = 1
        fields = ('id', 'name', 'description', 'status')
        read_only_fields = ('id', 'name')
