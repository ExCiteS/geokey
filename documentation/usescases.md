# Uses case scenarios

This document briefly describes common use case scenarios that the proposed platform is going to address. 

## Basic assumptions

### User Groups

User groups are used to grant rights to users to interact with the system. User groups can be assigned to projects as well as layers. They define what exactly a user is allowed to do within a project or a layer. Each user group provides information if the five following tasks can be executed:

1. **can_admin**: The user is an administrator for the project or layer and can therefore:
* Edit information, such as name, descriptions or status.
* Close projects or remove layers from a project.
* Add, edit and remove user groups.
* Create layers for a project.
* Perform tasks of all subsequent groups.

2. **can_edit**: The user is an editor of the project or layer and can therefore view, edit and remove all data in either all layers of the project or the respective layer. 

3. **can_contribute**: The user is allowed to view and add data to all layers in the project or the respective layer. 

4. **can_view**: The user is allowed to view the data of all layers in the project or the data of the respective layer. 

### Status of projects, layers, features and observations

## Project-related use-cases

### Create a new project

Every registered user of the platform can create new projects. New projects are issued with a name and a description. The project's status is automatically set to *active*. Further, standard user groups are assigned to the project:

1. **Administrators** can do every task described above within a project. The creator of a project is automatically added to the Administrators user group. This group cannot be removed from the project nor can it be edited. There must always be at least one member assigned to the group.
2. **Everyone** is a user group that applies to all unregistered users of the system as well as all registered users that are not member of any other user group assigned to the project. No users are explicitly assigned to the group. By default the group can only view information and data of the project. This group cannot be removed from the project and no users can be assigned to the project. 

### Update a project

Members of user groups that are allowed to administer the project can update the project's name, description and status. 

### Delete a project

Members of user groups that are allowed to administer the project can delete a project. When deleting a project the record is not removed from the database; rather the project's status is set to *deleted*, and can be recovered at a later time.

## Layer-related use-cases

### Create a new layer

Users that can administer a project are permitted to create and add new layers to a project. By default the user groups and permissions are applied from the parent project. 

### Update a layer

Members of user groups that are allowed to administer the layer or its parent project can update the layer's name, description and status. 

### Delete a layer

Members of user groups that are allowed to administer the layer or its parent project can delete a layer. When deleting a layer the record is not removed from the database; rather the project's status is set to *deleted*, and can be recovered at a later time.

### Create specialised user groups for a layer

As projects may have more than one layer, an administrator of a project might want to assign distinctive permissions to each of a project's layer. Therefore, individual user groups can be created for each layer. The assign new groups to a layer, first, two standard user groups (*Administrators* and *Everyone*) are created similar to a project's standard user groups. Both standard user groups of layers can be edited and removed from the layer. 

### Linking and cloning layers into projects

Layers can be assigned to more than one project. This ensures that data that are once collected can be re-used in other projects to reduce mapping efforts. There are to ways of assigning existing layers of one projects to another:

1. **Linking layers:** When a layer of Project A is linked to Project B the layer becomes available to users of both projects. Exactly one instance in the layer exists in the database. Contributions added to the layer by users of either Project A or Project B are available to users of both projects. 

2. **Cloning layers:** When a layer of Project A is cloned to Project B, a new instance of the layer -- including all features and observations -- is created in the system. The original layer and its clone are different entities. Therefore, contributions made to one of the layer within a project are only available to users of the same project. 

For both linked and cloned layers either the parent's projects user permissions apply or the individual layer level permissions apply. 

### Remove a layer from project

Members of user groups that are allowed to administer a layer's parent project can remove a layer from a project. The foreign keys are the removed from the database. In case, a layer has no more parent projects assigned, only the creator of a layer is able to view and administer the layer using the administration back-end interface. 