 /* ***********************************************
  * Based on changes to input[name="permission"}, the script displays (or hides)
  * a message that specific settings will be overwritten by project settings,
  * i.e. when all users can contribute to the project.
  *
  * Used in:
  * - templates/users/usergroup_permissions.html
  * ***********************************************/

(function () {
    var projectId = $('body').attr('data-project-id');
    var projectPrivate = $('body').attr('data-project-isprivate');
    var everyoneContributes = $('body').attr('data-everyone-contributes');

    function handlePermissionChange(event) {
        if ($(this).val() === 'read_only' && everyoneContributes !== 'false') {
            var add = '';
            if (projectPrivate !== 'True' && everyoneContributes === 'auth') {
                add = ', who have access to this project,';
            }
            $('form#permissions').before('<div class="alert alert-warning hint"><strong>Note:</strong> Currently, all users' + add + ' can contribute to the project. This setting overwrites permissions of individual user groups. If you plan to restrict contributing permissions to certain user groups, head to <a href="/admin/projects/' + projectId + '/settings/" class="alert-link">Project Settings</a> first and change the project permissions. </div>');
        } else {
            $('.hint').remove();
        }
    }

    $('form#permissions input[name="permission"]').change(handlePermissionChange);
}());
