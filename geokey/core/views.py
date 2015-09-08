from geokey.projects.models import Project
from geokey.core.decorators import handle_exceptions_for_admin


class ProjectContext(object):
    @handle_exceptions_for_admin
    def get_context_data(self, project_id, *args, **kwargs):
        """
        Returns the context containing the project instance.

        Parameters
        ----------
        project_id : int
            identifies the project in the data base

        Returns
        -------
        dict
        """
        project = Project.objects.as_admin(self.request.user, project_id)
        return super(ProjectContext, self).get_context_data(
            project=project,
            *args,
            **kwargs
        )
