"""Serializers for subsets."""

from rest_framework.serializers import ModelSerializer

from geokey.subsets.models import Subset


class SubsetSerializer(ModelSerializer):
    """Serializer for a subset."""

    class Meta:
        """Serializer meta."""

        model = Subset
        depth = 1
        fields = ('id', 'name', 'description', 'created_at')
