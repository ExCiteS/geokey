from django.db import models
from django.conf import settings

from django_pgjson.fields import JsonBField

from .base import STATUS
from .manager import GroupingManager, RuleManager


class Grouping(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    isprivate = models.BooleanField(default=False)
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )
    project = models.ForeignKey('projects.Project', related_name='groupings')

    objects = GroupingManager()

    class Meta:
        ordering = ['name']

    def get_where_clause(self):
        queries = [rule.get_query() for rule in self.rules.all()]

        if len(queries) > 0:
            query = ' OR '.join(queries)
            return query
        else:
            return None

    def data(self, user):
        """
        Provides access to all data accessable through the view. Uses the
        rules of the view to filter the data.
        """
        where_clause = self.get_where_clause()

        if where_clause is not None:
            if (self.project.can_moderate(user)):
                data = self.project.observations.for_moderator(user)
            else:
                data = self.project.observations.for_viewer(user)

            return data.extra(where=[where_clause])
        else:
            return self.project.observations.none()

    def delete(self):
        """
        Deletes the view by setting its status to DELETED.
        """
        self.status = STATUS.deleted
        self.save()

    def can_view(self, user):
        """
        Returns if the user can view data of the view.
        """
        if user.is_anonymous():
            return not self.isprivate

        return (not self.isprivate or
                self.project.is_admin(user) or
                self.usergroups.filter(
                    usergroup__users=user, can_view=True).exists())

    def can_read(self, user):
        """
        Returns if the user can read data of the view.
        """
        if user.is_anonymous():
            return not self.isprivate

        return (not self.isprivate or
                self.project.is_admin(user) or
                self.usergroups.filter(
                    usergroup__users=user, can_read=True).exists())

    def can_moderate(self, user):
        """
        Returns if the user can moderate data of the view.
        """
        if user.is_anonymous():
            return False

        return self.project.is_admin(user) or self.usergroups.filter(
            usergroup__users=user, usergroup__can_moderate=True).exists()


class Rule(models.Model):
    grouping = models.ForeignKey('Grouping', related_name='rules')
    category = models.ForeignKey('categories.Category')
    min_date = models.DateTimeField(null=True)
    max_date = models.DateTimeField(null=True)
    constraints = JsonBField(null=True, default=None)
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )

    objects = RuleManager()

    def get_query(self):
        """
        Returns the queryset filter for the Rule
        """
        queries = ['(category_id = %s)' % self.category.id]

        if self.min_date is not None:
            queries.append('(created_at >= to_date(\'' +
                           self.min_date.strftime('%Y-%m-%d %H:%I') +
                           '\', \'YYYY-MM-DD HH24:MI\'))')

        if self.max_date is not None:
            queries.append('(created_at <= to_date(\'' +
                           self.max_date.strftime('%Y-%m-%d %H:%I') +
                           '\', \'YYYY-MM-DD HH24:MI\'))')

        if self.constraints is not None:
            for key in self.constraints:
                field = self.category.fields.get_subclass(key=key)
                queries.append(field.get_filter(self.constraints[key]))

        return '(%s)' % ' AND '.join(queries)

    def delete(self):
        """
        Deletes the Filter by setting its status to DELETED.
        """
        self.status = STATUS.deleted
        self.save()
