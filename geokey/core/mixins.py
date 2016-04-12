"""Core mixins."""


class FilterMixin(object):
    """A mixin for filter."""

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
