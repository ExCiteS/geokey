from rest_framework import serializers

from .models import Application


class AppSerializer(serializers.ModelSerializer):
    """
    Serializer for Applications.
    """

    class Meta:
        model = Application
        depth = 1
        fields = ('id', 'name', 'description', 'status', 'download_url',
                  'redirect_url')
        read_only_fields = ('id',)
