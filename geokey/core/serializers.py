"""Core serializers."""

from rest_framework import serializers


class FieldSelectorSerializer(serializers.ModelSerializer):
    """
    Field selector serializer.

    Instances accept a `fields` keyword argument to set which fields shall be
    serialized.
    """

    def __init__(self, *args, **kwargs):
        """Initialization."""
        # Don't pass the `fields` argument to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass
        super(FieldSelectorSerializer, self).__init__(*args, **kwargs)

        if fields:
            # Drop any fields that are not specified in the `fields` argument
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field in existing - allowed:
                self.fields.pop(field)
