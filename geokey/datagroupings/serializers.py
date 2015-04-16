from geokey.core.serializers import FieldSelectorSerializer
from rest_framework.serializers import SerializerMethodField

from geokey.contributions.serializers import ContributionSerializer

from .models import Grouping


class GroupingSerializer(FieldSelectorSerializer):
    """
    Serializer for geokey.datagroupings.models.Grouping
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
        Returns all serialized contributions accessable through the data
        grouping.

        Parameter
        ---------
        obj : geokey.datagroupings.models.Grouping
            Grouping that is serialised

        Returns
        -------
        list
            serialised contribution objects
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

        Parameter
        ---------
        obj : geokey.datagroupings.models.Grouping
            Grouping that is serialised

        Returns
        -------
        int
            The number of contributions in the data grouping
        """
        user = self.context.get('user')
        return obj.data(user).count()
