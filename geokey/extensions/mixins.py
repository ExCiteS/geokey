"""Mixins for extensions."""

from geokey.superusertools.mixins import SuperuserMixin


class SuperuserMixin(SuperuserMixin):
    """A mixin for superuser."""

    exception_message = 'This extension is for superusers only.'
