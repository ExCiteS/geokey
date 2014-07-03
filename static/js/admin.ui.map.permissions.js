(function () {
    var projectId = $('body').attr('data-project-id');
    var viewId = $('body').attr('data-view-id');
    var messages = new Ui.MessageDisplay();

    function displayLoading() {
        $('#permissions .panel-heading:first-child').addClass('loading');
    }

    function removeLoading() {
        $('#permissions .panel-heading:first-child').removeClass('loading');
    }

    function handleViewActivateChange(event) {
        var target = $(event.target);
        var url = 'projects/' + projectId + '/usergroups/' + target.val() + '/';

        function handleError(response) {
            removeLoading();
            messages.showInlineError($('#permissions .panel-heading'), 'An error occurred while updating map permissions. Error text was: ' + response.responseJSON.error);
            target.prop('checked', !$(event.target).prop('checked'));
        }

        displayLoading();
        
        if (target.prop('checked')) {
            Control.Ajax.post(url + 'views/', removeLoading, handleError, {view: viewId});
        } else {
            Control.Ajax.del(url + 'views/' + viewId +'/', removeLoading, handleError);
        }
    }

    $('input[name="usergroup"]').change(handleViewActivateChange);
}());