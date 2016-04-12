"""Mixins for superuser tools."""


class SuperuserMixin(object):
    """A mixin for superuser."""

    exception_message = 'No rights to access superuser tools.'

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch the request.

        Check if user is a superuser, display an error message if not.

        Parameters
        ----------
        request : django.http.HttpRequest
            Object representing the request.

        Returns
        -------
        django.http.HttpResponse
        """
        if not request.user.is_superuser:
            return self.render_to_response({
                'error': 'Permission denied.',
                'error_description': self.exception_message
            })

        return super(SuperuserMixin, self).dispatch(request, *args, **kwargs)
