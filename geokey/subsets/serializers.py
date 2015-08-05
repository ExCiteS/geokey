from rest_framework.serializers import ModelSerializer
from .models import Subset


class SubsetSerializer(ModelSerializer):
    """
    Serialises Subset model instances
    """
    class Meta:
        model = Subset
        depth = 1
        fields = (
            'id', 'name', 'description', 'creator'
        )
