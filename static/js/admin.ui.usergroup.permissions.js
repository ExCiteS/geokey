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

    function displayLoading() {
        $('#viewgroups .panel-heading').addClass('loading');
    }

    function removeLoading() {
        $('#viewgroups .panel-heading').removeClass('loading');   
    }

    function handleActivateChange(event) {
        var target = $(event.target);
        var parent = target.parents('tr');

        function handleError(response) {
            removeLoading();
            messages.showInlineError($('#viewgroups .panel-heading'), 'An error occurred while updating the view group. Error text was: ' + response.responseJSON.error);
            target.prop('checked', !$(event.target).prop('checked'));
        }

        displayLoading();
        
        if (target.prop('checked')) {
            parent.find('input[type="checkbox"]').not('input[name="active"]').removeAttr('disabled');
            var data = getData(parent);
            data.view = parent.attr('data-view-id');

            Control.Ajax.post(url + 'views/', removeLoading, handleError, data);
        } else {
            parent.find('input[type="checkbox"]').not('input[name="active"]').attr('disabled', 'disabled');
            Control.Ajax.del(url + 'views/' + parent.attr('data-view-id') +'/', removeLoading, handleError);
        }
    }

    function handlePermissionChange(event) {
        var parent = $(event.target).parents('tr');
        var data = getData(parent);
        
        displayLoading();
        
        function handleError(response) {
            
            removeLoading();

            $(event.target).prop('checked', !$(event.target).prop('checked'));
            messages.showInlineError($('#viewgroups .panel-heading'), 'An error occurred while updating the view group. Error text was: ' + response.responseJSON.error);
        }
        
        Control.Ajax.put(url + 'views/' + parent.attr('data-view-id') +'/', removeLoading, handleError, data);
    }

    function handleContributeUpdateSuccess(response) {
        $('#can-contribute .panel-heading').removeClass('loading');
    }

    function handleContributeUpdateError(response) {
        $('#can-contribute .panel-heading').removeClass('loading');
        messages.showInlineError($('#can-contribute .panel-heading'), 'An error occurred while updating the user group. Error text was: ' + response.responseJSON.error);
        $('#can-contribute input[name="can_contribute"]').prop('checked', !$('#can-contribute input[name="can_contribute"]').prop('checked'));
    }

    function handleContributeChange(event) {
        var target = $(event.target);
        var data = {
            'can_contribute': target.prop('checked')
        };
        $('#can-contribute .panel-heading').addClass('loading');
        Control.Ajax.put(url, handleContributeUpdateSuccess, handleContributeUpdateError, data);
    }

    $('input[name="active"]').change(handleActivateChange);
    $('input[name="can_contribute"]').change(handleContributeChange);
    $('input[type="checkbox"]').not('input[name="can_contribute"]').not('input[name="active"]').change(handlePermissionChange);
}());