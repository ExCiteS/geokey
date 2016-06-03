"""Mixins for categories."""

from geokey.core.decorators import handle_exceptions_for_admin
from geokey.categories.models import Category, Field


class CategoryMixin(object):
    """A mixin for category."""

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, category_id, *args, **kwargs):
        """
        Return the context to render the view.

        Overwrite the method to add the project and the category to the
        context.

        Returns
        -------
        dict
            Context.
        """
        category = Category.objects.as_admin(
            self.request.user,
            project_id,
            category_id
        )
        return super(CategoryMixin, self).get_context_data(
            project=category.project,
            category=category,
            *args,
            **kwargs
        )


class FieldMixin(object):
    """A mixin for field."""

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, category_id, field_id,
                         *args, **kwargs):
        """
        Return the context to render the view.

        Overwrite the method to add the project, the category and the field to
        the context.

        Returns
        -------
        dict
            Context.
        """
        field = Field.objects.as_admin(
            self.request.user,
            project_id,
            category_id,
            field_id
        )
        return super(FieldMixin, self).get_context_data(
            project=field.category.project,
            category=field.category,
            field=field,
            is_display_field=(field == field.category.display_field),
            is_expiry_field=(field == field.category.expiry_field),
            *args,
            **kwargs
        )
