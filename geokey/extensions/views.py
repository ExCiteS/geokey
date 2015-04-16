class SuperuserMixin(object):
    """
    Mixin that checks if the user signed with the request is a superuser and
    displays the exception_message if not.
    """
    exception_message = 'This extension is for super users only.'

    def dispatch(self, request, *args, **kwargs):
        """
        Checks if user is superuser and displays the error message if not.

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request.

        Returns
        -------
        django.http.HttpResponse
            Rendered template
        """
        if not request.user.is_superuser:
            return self.render_to_response({
                'error_description': self.exception_message,
                'error': 'Permission denied.'
            })

        return super(SuperuserMixin, self).dispatch(request, *args, **kwargs)
