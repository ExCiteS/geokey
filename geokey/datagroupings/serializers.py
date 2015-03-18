from core.serializers import FieldSelectorSerializer
from rest_framework.serializers import SerializerMethodField

from contributions.serializers import ContributionSerializer

from .models import Grouping


class GroupingSerializer(FieldSelectorSerializer):
    """
    Serializer for Views.
    """
    contributions = SerializerMethodField('get_data')
    num_contributions = SerializerMethodField()

    class Meta:
        model = Grouping
        depth = 1
        fields = ('id', 'name', 'description', 'status',
                  'created_at', 'contributions', 'isprivate', 'status',
                  'num_contributions')
        read_only_fields = ('id', 'name', 'created_at')

    def get_data(self, obj):
        """
        Returns all serialized contributions accessable through the view.
        """
        user = self.context.get('user')

        serializer = ContributionSerializer(
            obj.data(user),
            many=True,
            context={'project': obj.project, 'user': user}
        )
        return serializer.data

    def get_num_contributions(self, obj):
        """
        Returns the number of contributions accessable through the view.
        """
        user = self.context.get('user')
        return obj.data(user).count()
