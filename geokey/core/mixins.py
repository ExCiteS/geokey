"""Core mixins."""


class FilterMixin(object):
    """A mixin for filter."""

    def remove_filter_field(self, field):
        """
        Remove a field from the filter.

        Parameters
        ----------
        field : geokey.categories.models.Field
            Represents the field of a category.
        """
        if self.filters:
            category_filter = self.filters.get(str(field.category.id), None)

            if category_filter:
                field_filter = category_filter.pop(field.key, None)

                if field_filter:
                    self.save()

    def save(self, *args, **kwargs):
        """Overwrite `save` to implement integrity ensurance."""
        self.where_clause = None

        if self.filters is not None:
            queries = []

            for key in self.filters:
                category = self.project.categories.get(pk=key)
                queries.append(category.get_query(self.filters[key]))

            if len(queries) > 0:
                query = ' OR '.join(queries)
                self.where_clause = query
            else:
                self.where_clause = 'FALSE'

        super(FilterMixin, self).save(*args, **kwargs)
