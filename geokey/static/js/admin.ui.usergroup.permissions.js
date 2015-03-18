(function () {
    var projectId = $('body').attr('data-project-id');
    var groupId = $('body').attr('data-group-id');
    var projectPrivate = $('body').attr('z`');
    var everyoneContributes = $('body').attr('data-everyone-contributes');
    var url = 'projects/' + projectId + '/usergroups/' + groupId + '/';

    function handleViewActivateChange(event) {
        var target = $(event.currentTarget);
        var groupingId = target.attr('name');

        function handleError(response) {
            target.toggleClass('active');
            var msg = 'An error occurred while updating map permissions. Error text was: ' + response.responseJSON.error;
            var html = $('<div class="bg-danger text-danger message"><span class="glyphicon glyphicon-remove"></span> ' + msg + '</div>');
            target.before(html);
            setTimeout(function () { html.remove(); }, 5000);
        }

        function handleSuccess(response) {
            var btnText = $('<span class="text-success">Grant access</span>');
            var msg = 'Access revoked.';
            if (target.hasClass('active')) {
                btnText = $('<span class="text-danger">Revoke access</span>');
                msg = 'Access granted.';
            }
            target.children().remove();
            target.append(btnText);

            var html = $('<div class="bg-success text-success message"><span class="glyphicon glyphicon-ok"></span> ' + msg + '</div>');
            target.before(html);
            setTimeout(function () { html.remove(); }, 5000);
        }

        if (target.hasClass('active')) {
            Control.Ajax.del(url + 'data-groupings/' + groupingId +'/', handleSuccess, handleError);
        } else {
            Control.Ajax.post(url + 'data-groupings/', handleSuccess, handleError, {grouping: groupingId});
        }
    }

    function grantAll() {
        $('button.grant-single:not(.active)').click();
    }

    function revokeAll() {
        $('button.grant-single.active').click();
    }

    $('button.grant-single').click(handleViewActivateChange);
    $('button#grant-all').click(grantAll);
    $('button#revoke-all').click(revokeAll);


    function updatePermissions(event) {
        event.preventDefault();

        var target = $(this);
        var value = target.serializeArray()[0].value;
        var data = {
            'can_contribute': false,
            'can_moderate': false
        };

        if (value === 'can_moderate') {
            data.can_contribute = true;
            data.can_moderate = true;
        } else if (value === 'can_contribute') {
            data.can_contribute = true;
        }

        function handleSuccess() {
            var html = $('<div class="bg-success text-success message"><span class="glyphicon glyphicon-ok"></span> Permissions have been updated.</div>');
            target.prepend(html);
            setTimeout(function () { html.remove(); }, 5000);

            $('input[name=permission]').removeAttr('checked');
            $('input#' + value).prop('checked', true);
            $('input#' + value).prop('defaultChecked', true);
        }

        function handleError(response) {
            event.target.reset();
            var msg = 'An error occurred while updating the permissions. Error text was: ' + response.responseJSON.error;
            var html = $('<div class="bg-danger text-danger message"><span class="glyphicon glyphicon-ok"></span> ' + msg + '</div>');
            target.prepend(html);
            setTimeout(function () { html.remove(); }, 5000);
        }

        Control.Ajax.put(url, handleSuccess, handleError, data);
    }

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

    $('form#permissions').submit(updatePermissions);
    $('form#permissions input[name="permission"]').change(handlePermissionChange);
}());
