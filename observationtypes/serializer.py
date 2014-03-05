from rest_framework import serializers

from .models import ObservationType, Field, NumericField, LookupField


class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        depth = 1
        fields = ('id', 'name', 'key', 'description', 'status', 'required')
        read_only_fields = ('id', 'name', 'key')


class FieldUpdateSerializer(FieldSerializer):
    description = serializers.CharField(required=False)


class NumericFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = NumericField
        depth = 1
        fields = (
            'id', 'name', 'key', 'description', 'status', 'required',
            'minval', 'maxval'
        )
        read_only_fields = ('id', 'name', 'key')


class NumericFieldUpdateSerializer(NumericFieldSerializer):
    description = serializers.CharField(required=False)


class LookupFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = LookupField
        depth = 1
        fields = (
            'id', 'name', 'key', 'description', 'status', 'required',
            'lookupvalues'
        )
        read_only_fields = ('id', 'name', 'key')


class ObservationTypeSerializer(serializers.ModelSerializer):
    # fields = FieldSerializer(many=True, read_only=True)

    class Meta:
        model = ObservationType
        depth = 1
        fields = ('id', 'name', 'description', 'status')
        read_only_fields = ('id', 'name')


class ObservationTypeUpdateSerializer(ObservationTypeSerializer):
    description = serializers.CharField(required=False)
