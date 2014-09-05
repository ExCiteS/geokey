from rest_framework import serializers

from core.serializers import FieldSelectorSerializer

from .models import (
    ObservationType, Field, NumericField, LookupField, LookupValue
)


class FieldSerializer(serializers.ModelSerializer):
    """
    Serializer for fields.
    Used in .views.FieldApiDetail
    """
    fieldtype = serializers.Field()

    class Meta:
        model = Field
        depth = 1
        fields = (
            'id', 'name', 'key', 'fieldtype', 'description', 'status',
            'required'
        )
        read_only_fields = ('id', 'name', 'key')
        write_only_fields = ('status',)


class NumericFieldSerializer(serializers.ModelSerializer):
    """
    Serializer for numeric fields.
    Used in .views.FieldApiDetail
    """
    fieldtype = serializers.Field()

    class Meta:
        model = NumericField
        depth = 1
        fields = (
            'id', 'name', 'key', 'fieldtype', 'description', 'status',
            'required', 'minval', 'maxval'
        )
        read_only_fields = ('id', 'name', 'key')
        write_only_fields = ('status',)


class LookupValueSerializer(serializers.ModelSerializer):
    """
    Serializer for lookup value.
    Used in .views.FieldApiLookups
    """
    class Meta:
        model = LookupValue
        fields = ('id', 'name')

    def field_to_native(self, obj, field_name):
        return [
            self.to_native(item)
            for item in obj.lookupvalues.filter(status='active')
        ]


class LookupFieldSerializer(serializers.ModelSerializer):
    """
    Serializer for lookup fields.
    Used in .views.FieldApiLookups
    """
    lookupvalues = LookupValueSerializer(many=True, read_only=True)
    fieldtype = serializers.Field()

    class Meta:
        model = LookupField
        depth = 1
        fields = (
            'id', 'name', 'key', 'fieldtype', 'description', 'status',
            'required', 'lookupvalues'
        )
        read_only_fields = ('id', 'name', 'key')
        write_only_fields = ('status',)


class FieldObjectRelatedField(serializers.RelatedField):
    def to_native(self, value):
        if isinstance(value, NumericField):
            serializer = NumericFieldSerializer(value)
        elif isinstance(value, LookupField):
            serializer = LookupFieldSerializer(value)
        else:
            serializer = FieldSerializer(value)

        return serializer.data

    def field_to_native(self, obj, field_name):
        return [
            self.to_native(item)
            for item in obj.fields.active().select_subclasses()
        ]


class ObservationTypeSerializer(FieldSelectorSerializer):
    """
    Serializer for observation types. Used for AJAX API updates.
    Used in .views.ObservationTypeAdminDetailView
    """
    fields = FieldObjectRelatedField(many=True, read_only=False)

    class Meta:
        model = ObservationType
        depth = 1
        fields = ('id', 'name', 'description', 'status', 'fields')
        read_only_fields = ('id', 'name')
