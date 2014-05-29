import json

from django.db import models
from django.db.models import Q
from django.conf import settings

from django_hstore import hstore

from .base import STATUS
from .manager import ViewManager, RuleManager


class View(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    isprivate = models.BooleanField(default=False)
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )
    project = models.ForeignKey('projects.Project', related_name='views')

    objects = ViewManager()

    @property
    def data(self):
        queries = [rule.get_query() for rule in self.rules.all()]

        if len(queries) > 0:
            query = queries.pop()
            for item in queries:
                query |= item
            return self.project.observations.filter(query)

        else:
            return []

    def delete(self):
        """
        Deletes the view by setting its status to DELETED.
        """
        self.status = STATUS.deleted
        self.save()

    def can_view(self, user):
        return self.project.is_admin(user) or self.usergroups.filter(usergroup__users=user, can_view=True).exists()

    def can_read(self, user):
        return self.project.is_admin(user) or self.usergroups.filter(usergroup__users=user, can_read=True).exists()

    def can_moderate(self, user):
        return self.project.is_admin(user) or self.usergroups.filter(usergroup__users=user, can_moderate=True).exists()


class Rule(models.Model):
    view = models.ForeignKey('View', related_name='rules')
    observation_type = models.ForeignKey('observationtypes.ObservationType')
    filters = hstore.DictionaryField(db_index=True, null=True, default=None)
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )

    objects = RuleManager()

    def get_query(self):
        queries = [Q(observationtype=self.observation_type)]

        if self.filters is not None:
            for key in self.filters:
                try:
                    rule_filter = json.loads(self.filters[key])
                except ValueError:
                    rule_filter = self.filters[key]

                field = self.observation_type.fields.get_subclass(key=key)
                queries.append(field.get_filter(rule_filter))

        query = queries.pop()
        for item in queries:
            query &= item
        return query

    def delete(self):
        """
        Deletes the Filter by setting its status to DELETED.
        """
        self.status = STATUS.deleted
        self.save()
