class SuperuserMixin(object):
    exception_message = 'This extension is for super users only.'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return self.render_to_response({
                'error_description': self.exception_message,
                'error': 'Permission denied.'
            })

        return super(SuperuserMixin, self).dispatch(request, *args, **kwargs)
