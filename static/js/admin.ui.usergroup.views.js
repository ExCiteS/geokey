(function () {
    var projectId = $('body').attr('data-project-id');
    var groupId = $('body').attr('data-group-id');
    var url = 'projects/' + projectId + '/usergroups/' + groupId + '/';
    var messages = new Ui.MessageDisplay();

    function getData(view) {
        return {
            can_view: view.find('input[name="can_view"]').prop('checked'),
            can_read: view.find('input[name="can_read"]').prop('checked'),
            can_moderate: view.find('input[name="can_moderate"]').prop('checked')
        };
    }


    function handleActivateChange(event) {
        var target = $(event.target);
        var parent = target.parents('tr');

        function handleError(response) {
            messages.showPanelError($('#viewgroups'), 'An error occurred while updating the view group. Error text was: ' + response.responseJSON.error);
            target.prop('checked', !$(event.target).prop('checked'));
        }

        if (target.prop('checked')) {
            parent.find('input[type="checkbox"]').not('input[name="active"]').removeAttr('disabled');
            var data = getData(parent);
            data.view = parent.attr('data-view-id');

            Control.Ajax.post(url + 'views/', null, handleError, data);
        } else {
            parent.find('input[type="checkbox"]').not('input[name="active"]').attr('disabled', 'disabled');
            Control.Ajax.del(url + 'views/' + parent.attr('data-view-id') +'/', null, handleError);
        }
    }

    function handlePermissionChange(event) {
        var parent = $(event.target).parents('tr');
        var data = getData(parent);

        function handleError(response) {
            $(event.target).prop('checked', !$(event.target).prop('checked'));
            messages.showPanelError($('#viewgroups'), 'An error occurred while updating the view group. Error text was: ' + response.responseJSON.error);
        }

        Control.Ajax.put(url + 'views/' + parent.attr('data-view-id') +'/', null, handleError, data);
    }

    $('input[name="active"]').change(handleActivateChange);
    $('input[type="checkbox"]').not('input[name="can_contribute"]').not('input[name="active"]').change(handlePermissionChange);
}());