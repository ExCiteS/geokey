from rest_framework import serializers

from .models import ObservationType, Field, NumericField, LookupField


class FieldSerializer(serializers.ModelSerializer):
    """
    Serializer for fields.
    Used in .views.FieldApiDetail
    """
    class Meta:
        model = Field
        depth = 1
        fields = ('id', 'name', 'key', 'description', 'status', 'required')
        read_only_fields = ('id', 'name', 'key')


class NumericFieldSerializer(serializers.ModelSerializer):
    """
    Serializer for numeric fields.
    Used in .views.FieldApiDetail
    """
    class Meta:
        model = NumericField
        depth = 1
        fields = (
            'id', 'name', 'key', 'description', 'status', 'required',
            'minval', 'maxval'
        )
        read_only_fields = ('id', 'name', 'key')


class LookupFieldSerializer(serializers.ModelSerializer):
    """
    Serializer for lookup fields.
    Used in .views.FieldApiLookups
    """
    class Meta:
        model = LookupField
        depth = 1
        fields = (
            'id', 'name', 'key', 'description', 'status', 'required',
            'lookupvalues'
        )
        read_only_fields = ('id', 'name', 'key')


class ObservationTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for observation types. Used for AJAX API updates.
    Used in .views.ObservationTypeAdminDetailView
    """
    class Meta:
        model = ObservationType
        depth = 1
        fields = ('id', 'name', 'description', 'status')
        read_only_fields = ('id', 'name')
