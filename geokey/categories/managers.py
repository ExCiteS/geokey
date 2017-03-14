"""Managers for categories."""

from django.db import models
from django.core.exceptions import PermissionDenied

from model_utils.managers import InheritanceManager

from geokey.projects.models import Project

from .base import STATUS


class ActiveMixin(object):
    """
    Mixin to provide a queryset method filtering for all instances of the
    model that have status active.
    """
    def active(self):
        """
        Returns all active instances

        Returns
        -------
        django.db.models.Queryset
            All active instances
        """
        return self.get_queryset().filter(status=STATUS.active)


class CategoryManager(ActiveMixin, models.Manager):
    """
    Adds category-specific manager methods.
    """
    def get_queryset(self):
        """
        Returns all categories

        Returns
        -------
        django.db.models.Queryset
            All categories, excluding deleted
        """
        return super(
            CategoryManager,
            self
        ).get_queryset().exclude(status=STATUS.deleted)

    def get_list(self, user, project_id):
        """
        Returns all category objects the user is allowed to access. Project
        admins can access all categories, other users will get access to
        active categories only.

        Parameters
        ----------
        user : geokey.users.models.User
            User the categories are queried for
        project_id : int
            ID identifying the project in the database

        Returns
        -------
        django.db.models.Queryset
            Queryset of all categories the user is allowed to access
        """
        project = Project.objects.get_single(user, project_id)
        if (project.is_admin(user)):
            return project.categories.all()
        else:
            return project.categories.active()

    def get_single(self, user, project_id, category_id):
        """
        Returns all a single category.

        Parameters
        ----------
        user : geokey.users.models.User
            User the categories are queried for
        project_id : int
            ID identifying the project in the database
        category_id : int
            ID identifying the category in the database

        Returns
        -------
        geokey.categories.models.Category

        Raises
        ------
        PermissionDenied
            if the user is not eligable to access the category
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
        Returns all a single category for a project admin.

        Parameters
        ----------
        user : geokey.users.models.User
            User the categories are queried for
        project_id : int
            ID identifying the project in the database
        category_id : int
            ID identifying the category in the database

        Returns
        -------
        geokey.categories.models.Category

        Raises
        ------
        PermissionDenied
            if the user is not an admin of the project
        """
        return Project.objects.as_admin(
            user, project_id
            ).categories.get(pk=category_id)

    def create(self, *args, **kwargs):
        """
        Creates a new category. Overwrites method to set the order of the
        category in the list of categories.

        Returns
        -------
        geokey.categories.models.Category
            The newly created category
        """

        return super(CategoryManager, self).create(
            order=kwargs.get('project').categories.count(), *args, **kwargs)



class FieldManager(ActiveMixin, InheritanceManager):
    """
    Adds field-specific manager methods.
    """
    use_for_related_fields = True

    def get_queryset(self):
        """
        Returns all field subclasses ordered by `order` within the category.

        Returns
        -------
        django.db.models.Queryset
            All fields, excluding deleted
        """
        return super(FieldManager, self).get_queryset().order_by(
            'order').select_subclasses()

    def get_list(self, user, project_id, category_id):
        """
        Returns all fields the user is allowed to access.

        Parameters
        ----------
        user : geokey.users.models.User
            User the categories are queried for
        project_id : int
            ID identifying the project in the database
        category_id : int
            ID identifying the category in the database

        Returns
        -------
        django.db.models.Queryset
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
        Returns all a single field.

        Parameters
        ----------
        user : geokey.users.models.User
            User the categories are queried for
        project_id : int
            ID identifying the project in the database
        category_id : int
            ID identifying the category in the database
        field_id : int
            ID identifying the field in the database

        Returns
        -------
        geokey.categories.models.Field sublcass
            i.e. if you query for a TextField instance
            geokey.categories.models.TextField is return

        Raises
        ------
        PermissionDenied
            if the user is not eligable to access the field
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
        Returns all a single field for a project admin.

        Parameters
        ----------
        user : geokey.users.models.User
            User the categories are queried for
        project_id : int
            ID identifying the project in the database
        category_id : int
            ID identifying the category in the database
        field_id : int
            ID identifying the field in the database

        Returns
        -------
        geokey.categories.models.Field sublcass
            i.e. if you query for a TextField instance
            geokey.categories.models.TextField is return

        Raises
        ------
        PermissionDenied
            if the user is not admin of the project
        """
        return Project.objects.as_admin(
            user, project_id).categories.get(
            pk=category_id).fields.get_subclass(pk=field_id)


class LookupQuerySet(models.query.QuerySet):
    """
    QuerySet for models having a field status. User by ActiveManager.
    """
    def active(self):
        """
        Returns all active instances

        Returns
        -------
        Queryset of all active instances
        """
        return self.filter(status=STATUS.active)


class LookupValueManager(models.Manager):
    """
    Manager for models having a field status. Is required to render active
    items only in templates.
    """
    use_for_related_fields = True

    def get_queryset(self):
        """
        Returns the Queryset

        Returns
        -------
        django.db.models.Queryset
            all lookupvalues
        """
        return LookupQuerySet(self.model)

    def active(self, *args, **kwargs):
        """
        Returns all active instances

        Returns
        -------
        django.db.models.Queryset
            All active instances
        """
        return self.get_queryset().active(*args, **kwargs)
