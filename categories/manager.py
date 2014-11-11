from django.db import models
from django.core.exceptions import PermissionDenied

from model_utils.managers import InheritanceManager

from datagroupings.models import Grouping, Rule
from projects.models import Project

from .base import STATUS


class ActiveMixin(object):
    """
    Mixin to provide a queryset method filtering for all instances of the
    model that have status active.
    """
    def active(self, *args, **kwargs):
        """
        Returns a queryset of all active instances
        """
        return self.get_query_set().filter(status=STATUS.active)


class CategoryManager(ActiveMixin, models.Manager):
    def get_query_set(self):
        """
        Returns the QuerySet
        """
        return super(
            CategoryManager,
            self
        ).get_query_set().exclude(status=STATUS.deleted)

    def get_list(self, user, project_id):
        """
        Returns all category objects the user is allowed to access
        """
        project = Project.objects.get_single(user, project_id)
        if (project.is_admin(user)):
            return project.categories.all()
        else:
            return project.categories.active()

    def get_single(self, user, project_id, category_id):
        """
        Returns all a single category. Raises PermissionDenied if user
        is not eligable to access the category.
        """
        category = Project.objects.get_single(
            user, project_id).categories.get(pk=category_id)

        if (category.status == STATUS.active or
                category.project.is_admin(user)):
            return category
        else:
            raise PermissionDenied('You are not allowed to access this '
                                   'category')

    def as_admin(self, user, project_id, category_id):
        """
        Returns all a single category for an project admin.
        """
        return Project.objects.as_admin(
            user, project_id
            ).categories.get(pk=category_id)

    def create(self, create_grouping=False, *args, **kwargs):
        category = super(CategoryManager, self).create(*args, **kwargs)

        if create_grouping:
            grouping = Grouping.objects.create(
                name=category.name,
                description='All contributions of category %s.' % (
                    category.name),
                project=category.project,
                creator=category.creator
            )

            Rule.objects.create(
                grouping=grouping,
                category=category
            )

        return category


class FieldManager(ActiveMixin, InheritanceManager):
    use_for_related_fields = True

    def get_query_set(self):
        return super(FieldManager, self).get_query_set().order_by(
            'order').select_subclasses()

    def get_list(self, user, project_id, category_id):
        """
        Returns all fields the user is allowed to access.
        """
        project = Project.objects.get_single(user, project_id)

        if project.is_admin(user):
            return project.categories.get(
                pk=category_id).fields.all().select_subclasses()
        else:
            category = project.categories.get(
                pk=category_id)
            if category.status == STATUS.active:
                return category.fields.active().select_subclasses()

    def get_single(self, user, project_id, category_id, field_id):
        """
        Returns a single field
        """
        project = Project.objects.get_single(user, project_id)
        category = project.categories.get(pk=category_id)
        field = category.fields.get_subclass(pk=field_id)

        if project.is_admin(user):
            return field
        else:
            if category.status == STATUS.active:
                if field.status == STATUS.active:
                    return field
                else:
                    raise PermissionDenied('You are not allowed to access '
                                           'this field')
            else:
                raise PermissionDenied('You are not allowed to access this '
                                       'category')

    def as_admin(self, user, project_id, category_id, field_id):
        """
        Returns all a single field for an project admin.
        """
        return Project.objects.as_admin(
            user, project_id).categories.get(
            pk=category_id).fields.get_subclass(pk=field_id)


class LookupQuerySet(models.query.QuerySet):
    """
    QuerySet for models having a field status. User by ActiveManager.
    """
    def active(self):
        return self.filter(status=STATUS.active)


class LookupValueManager(models.Manager):
    """
    Manager for models having a field status. Is required to render active
    items only in templates.
    """
    use_for_related_fields = True

    def get_query_set(self):
        return LookupQuerySet(self.model)

    def active(self, *args, **kwargs):
        return self.get_query_set().active(*args, **kwargs)
