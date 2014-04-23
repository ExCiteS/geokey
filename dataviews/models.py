import json

from django.db import models
from django.conf import settings

from django_hstore import hstore

from contributions.models import Observation

from .base import STATUS
from .manager import ViewManager, ViewGroupManager, RuleManager


class View(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )
    project = models.ForeignKey('projects.Project', related_name='views')

    objects = ViewManager()

    @property
    def data(self):
        # sql = 'SELECT * FROM public.contributions_observation LEFT JOIN (SELECT * FROM public.contributions_observationdata GROUP BY contributions_observationdata.id HAVING max(created_at) = contributions_observationdata.created_at) as foo on (contributions_observation.id = observation_id) WHERE '

        # for idx, rule in enumerate(self.rules.all()):
        #     sub_sql = '(observationtype_id=%s' % rule.observation_type.id

        #     for key in rule.filters:
        #         field = rule.observation_type.fields.get_subclass(key=key)
        #         try:
        #             rule_filter = json.loads(rule.filters[key])
        #         except ValueError:
        #             rule_filter = rule.filters[key]

        #         sub_sql = sub_sql + ' AND ' + field.get_sql_filter(rule_filter)

        #     sub_sql = sub_sql + ')'

        #     if idx > 0:
        #         sql = sql + ' OR '

        #     sql = sql + sub_sql

        # return list(self.project.observations.raw(sql))
        querysets = []

        for rule in self.rules.all():
            result = self.project.observations.filter(
                observationtype=rule.observation_type)

            for key in rule.filters:
                try:
                    rule_filter = json.loads(rule.filters[key])
                except ValueError:
                    rule_filter = rule.filters[key]

                field = rule.observation_type.fields.get_subclass(key=key)
                result = (x for x in result if field.filter(x, rule_filter))

            querysets.append(result)

        return [item for sublist in querysets for item in sublist]

    def delete(self):
        """
        Deletes the view by setting its status to DELETED.
        """
        self.status = STATUS.deleted
        self.save()


class ViewGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    can_edit = models.BooleanField(default=False)
    can_read = models.BooleanField(default=False)
    can_view = models.BooleanField(default=True)
    view = models.ForeignKey('View', related_name='viewgroups')
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )

    objects = ViewGroupManager()

    def delete(self):
        """
        Deletes the view by setting its status to DELETED.
        """
        self.status = STATUS.deleted
        self.save()


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

    def delete(self):
        """
        Deletes the Filter by setting its status to DELETED.
        """
        self.status = STATUS.deleted
        self.save()
