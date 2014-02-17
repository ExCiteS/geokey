from opencomap.apps.backend.models.project import Project
from opencomap.apps.backend.models.usergroup import UserGroup


def createProject(name, description, creator, isprivate=False):
    """
    Creates a new project, adds to user groups to the projects and adds the
    creator to the group of project administrators. Returns the created
    project.

    :name: The name of the project.
    :description: The description of the project.
    :creator: The user who creates the project.
    """

    adminGroup = UserGroup(name='Administrators')
    adminGroup.save()
    adminGroup.addUsers(creator)
    adminGroup.save()
    everyoneGroup = UserGroup(name='Contributors')
    everyoneGroup.save()

    project = Project(
        name=name, description=description, admins=adminGroup,
        contributors=everyoneGroup, creator=creator, isprivate=isprivate
    )
    project.save()

    return project
