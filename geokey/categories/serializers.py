"""Serializers for categories."""

from rest_framework.serializers import (
    ModelSerializer, ReadOnlyField, SerializerMethodField
)

from geokey.core.serializers import FieldSelectorSerializer
from geokey.categories.models import (
    Category, Field, TextField, NumericField,
    LookupField, LookupValue, MultipleLookupField, MultipleLookupValue
)


class FieldSerializer(ModelSerializer):
    """Serializer for fields."""

    fieldtype = ReadOnlyField()
    is_displayfield = SerializerMethodField()

    class Meta:
        """Meta information for serializer."""

        model = Field
        depth = 1
        fields = ('id', 'status', 'fieldtype', 'name', 'description', 'key',
                  'required', 'is_displayfield')
        read_only_fields = ('id', 'name', 'key')

    def get_is_displayfield(self, field):
        """
        Return whether the field is set as a display field for the category.

        Parameters
        ----------
        field : geokey.categories.models.field
            Field that is being serialized

        Returns
        -------
        Boolean
        """
        if field.category.display_field == field:
            return True
        else:
            return False


class TextFieldSerializer(FieldSerializer):
    """Serializer for text fields."""

    class Meta:
        """Meta information for serializer."""

        model = TextField
        depth = 1
        fields = ('id', 'status', 'fieldtype', 'name', 'description', 'key',
                  'required', 'is_displayfield', 'maxlength', 'textarea')
        read_only_fields = ('id', 'name', 'key')


class NumericFieldSerializer(FieldSerializer):
    """Serializer for numeric fields."""

    class Meta:
        """Meta information for serializer."""

        model = NumericField
        depth = 1
        fields = ('id', 'status', 'fieldtype', 'name', 'description', 'key',
                  'required', 'is_displayfield', 'minval', 'maxval')
        read_only_fields = ('id', 'name', 'key')


class LookupValueSerializer(ModelSerializer):
    """Serializer for single lookupvalue."""

    class Meta:
        """Meta information for serializer."""

        model = LookupValue
        fields = ('id', 'name', 'symbol')


class MultipleLookupValueSerializer(ModelSerializer):
    """Serializer for multiple lookup value."""

    class Meta:
        """Meta information for serializer."""

        model = MultipleLookupValue
        fields = ('id', 'name', 'symbol')


class BaseLookupSerializer(object):
    """Base serializer for both single and multiple lookup fields."""

    def get_lookupvalues(self, field):
        """
        Return serialized lookupvalues.

        Parameters
        ----------
        field : geokey.categories.models.Field
            Field of which lookupvalues are serialised

        Returns
        -------
        List
            Serialized lookupvalues
        """
        values = field.lookupvalues.filter(status='active')

        if isinstance(field, LookupField):
            serializer = LookupValueSerializer(values, many=True)
        elif isinstance(field, MultipleLookupField):
            serializer = MultipleLookupValueSerializer(values, many=True)

        return serializer.data


class LookupFieldSerializer(FieldSerializer, BaseLookupSerializer):
    """Serializer for single lookup fields."""

    lookupvalues = SerializerMethodField()

    class Meta:
        """Meta information for serializer."""

        model = LookupField
        depth = 1
        fields = ('id', 'status', 'fieldtype', 'name', 'description', 'key',
                  'required', 'is_displayfield', 'lookupvalues')
        read_only_fields = ('id', 'name', 'key')
        write_only_fields = ('status',)


class MultipleLookupFieldSerializer(FieldSerializer, BaseLookupSerializer):
    """Serializer for multiple lookup fields."""

    lookupvalues = SerializerMethodField()

    class Meta:
        """Meta information for serializer."""

        model = LookupField
        depth = 1
        fields = ('id', 'status', 'fieldtype', 'name', 'description', 'key',
                  'required', 'is_displayfield', 'lookupvalues')
        read_only_fields = ('id', 'name', 'key')
        write_only_fields = ('status',)


class CategorySerializer(FieldSelectorSerializer):
    """Serializer for categories."""

    fields = SerializerMethodField('get_fields_serialized')

    class Meta:
        """Meta information for serializer."""

        model = Category
        depth = 1
        fields = ('id', 'status', 'created_at', 'name', 'description',
                  'colour', 'symbol', 'order', 'fields')
        read_only_fields = ('id', 'name', 'created_at')

    def get_fields_serialized(self, category):
        """
        Return a list of serialized fields for the category.

        Parameters
        ----------
        category : geokey.categories.models.category
            Category of which field are serialized

        Returns
        -------
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
