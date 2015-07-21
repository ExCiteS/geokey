from rest_framework.serializers import ModelSerializer
from .models import Subset


class SubsetSerializer(ModelSerializer):
    class Meta:
        model = Subset
        depth = 1
        fields = (
            'id', 'name', 'description', 'created_at', 'creator'
        )
