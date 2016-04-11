"""Serializers for categories."""

from rest_framework.serializers import (
    ModelSerializer, ReadOnlyField, SerializerMethodField
)

from geokey.core.serializers import FieldSelectorSerializer

from .models import (
    Category, Field, TextField, NumericField, LookupField, LookupValue,
    MultipleLookupField, MultipleLookupValue
)


class FieldSerializer(ModelSerializer):
    """
    Serializer for fields.
    Used in .views.FieldApiDetail
    """
    fieldtype = ReadOnlyField()

    class Meta:
        model = Field
        depth = 1
        fields = (
            'id', 'name', 'key', 'fieldtype', 'description', 'status',
            'required', 'status'
        )
        read_only_fields = ('id', 'name', 'key')


class TextFieldSerializer(ModelSerializer):
    """
    Serializer for text fields.
    Used in .views.FieldApiDetail
    """
    fieldtype = ReadOnlyField()

    class Meta:
        model = TextField
        depth = 1
        fields = (
            'id', 'name', 'key', 'fieldtype', 'description', 'status',
            'required', 'status', 'maxlength', 'textarea'
        )
        read_only_fields = ('id', 'name', 'key')


class NumericFieldSerializer(ModelSerializer):
    """
    Serializer for numeric fields.
    Used in .views.FieldApiDetail
    """
    fieldtype = ReadOnlyField()

    class Meta:
        model = NumericField
        depth = 1
        fields = (
            'id', 'name', 'key', 'fieldtype', 'description', 'status',
            'required', 'minval', 'maxval'
        )
        read_only_fields = ('id', 'name', 'key')


class LookupValueSerializer(ModelSerializer):
    """
    Serializer for lookup value.
    Used in .views.FieldApiLookups
    """
    class Meta:
        model = LookupValue
        fields = ('id', 'name', 'symbol')


class MultipleLookupValueSerializer(ModelSerializer):
    """
    Serializer for lookup value.
    Used in .views.FieldApiLookups
    """
    class Meta:
        model = MultipleLookupValue
        fields = ('id', 'name', 'symbol')


class BaseLookupSerializer(object):
    """
    Base class for LookupFieldSerializer and MultipleLookupFieldSerializer
    """
    def get_lookupvalues(self, field):
        """
        Returns serialised Lookupvalues

        Parameter
        ---------
        field : geokey.categories.models.Field
            Field which lookupvalues are serialised

        Return
        ------
        List
            Serialized lookupvalues
        """
        values = field.lookupvalues.filter(status='active')

        if isinstance(field, LookupField):
            serializer = LookupValueSerializer(values, many=True)
        elif isinstance(field, MultipleLookupField):
            serializer = MultipleLookupValueSerializer(values, many=True)

        return serializer.data


class LookupFieldSerializer(ModelSerializer, BaseLookupSerializer):
    """
    Serializer for lookup fields.
    Used in .views.FieldApiLookups
    """
    lookupvalues = SerializerMethodField()
    fieldtype = ReadOnlyField()

    class Meta:
        model = LookupField
        depth = 1
        fields = (
            'id', 'name', 'key', 'fieldtype', 'description', 'status',
            'required', 'lookupvalues'
        )
        read_only_fields = ('id', 'name', 'key')
        write_only_fields = ('status',)


class MultipleLookupFieldSerializer(ModelSerializer, BaseLookupSerializer):
    """
    Serializer for lookup fields.
    Used in .views.FieldApiLookups
    """
    lookupvalues = SerializerMethodField()
    fieldtype = ReadOnlyField()

    class Meta:
        model = LookupField
        depth = 1
        fields = (
            'id', 'name', 'key', 'fieldtype', 'description', 'status',
            'required', 'lookupvalues'
        )
        read_only_fields = ('id', 'name', 'key')
        write_only_fields = ('status',)


class CategorySerializer(FieldSelectorSerializer):
    """
    Serializer for observation types. Used for AJAX API updates.
    Used in .views.ObservationTypeAdminDetailView
    """
    fields = SerializerMethodField('get_fields_serialized')

    class Meta:
        model = Category
        depth = 1
        fields = ('id', 'name', 'description', 'status', 'fields', 'colour',
                  'created_at', 'symbol', 'order')
        read_only_fields = ('id', 'name', 'created_at')

    def get_fields_serialized(self, category):
        """
        Returns a list of serialized fields for the category

        Parameter
        ---------
        category : geokey.categories.models.category
            Category which field are serialized

        Return
        ------
        List
            Serialized fields
        """
        fields = []

        for field in category.fields.filter(status='active'):
            if isinstance(field, TextField):
                serializer = TextFieldSerializer(field)
            elif isinstance(field, NumericField):
                serializer = NumericFieldSerializer(field)
            elif isinstance(field, LookupField):
                serializer = LookupFieldSerializer(field)
            elif isinstance(field, MultipleLookupField):
                serializer = MultipleLookupFieldSerializer(field)
            else:
                serializer = FieldSerializer(field)

            fields.append(serializer.data)

        return fields
