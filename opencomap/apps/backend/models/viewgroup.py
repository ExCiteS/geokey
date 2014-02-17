from django.db import models

from opencomap.apps.backend.models.usergroup import UserGroup


class ViewGroup(UserGroup):
    can_edit = models.BooleanField(default=False)
    can_read = models.BooleanField(default=False)
    can_view = models.BooleanField(default=True)
    view = models.ForeignKey('backend.View')

    class Meta:
        app_label = 'backend'

    def update(self, description=None, can_edit=None,
               can_read=None, can_view=None):

        if description:
            self.description = description
        if can_edit is not None:
            self.can_edit = can_edit
        if can_read is not None:
            self.can_read = can_read
        if can_view is not None:
            self.can_view = can_view

        self.save()

        return self
