from rest_framework import serializers

from .models import ObservationType


class ObservationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservationType
        depth = 1
        fields = ('id', 'name', 'description', 'status')
        read_only_fields = ('id', 'name')


class ObservationTypeUpdateSerializer(ObservationTypeSerializer):
    def __init__(self, *args, **kwargs):
        super(ObservationTypeUpdateSerializer, self).__init__(*args, **kwargs)
        self.fields['description'].required = False
