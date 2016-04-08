"""All views for extensions."""

from geokey.superusertools.views import SuperuserMixin


class SuperuserMixin(SuperuserMixin):
    """A mixin for superuser."""

    exception_message = 'This extension is for superusers only.'
