(function () {
    var projectId = $('body').attr('data-project-id');
    var groupId = $('body').attr('data-group-id');
    var url = 'projects/' + projectId + '/usergroups/' + groupId + '/';
    var messages = new Ui.MessageDisplay();

    function displayLoading() {
        $('#permissions .panel-heading:first-child').addClass('loading');
    }

    function removeLoading() {
        $('#permissions .panel-heading:first-child').removeClass('loading');
    }

    function handleViewActivateChange(event) {
        var target = $(event.target);

        function handleError(response) {
            removeLoading();
            messages.showInlineError($('#permissions .panel-heading'), 'An error occurred while updating view permissions. Error text was: ' + response.responseJSON.error);
            target.prop('checked', !$(event.target).prop('checked'));
        }

        displayLoading();
        
        if (target.prop('checked')) {
            Control.Ajax.post(url + 'views/', removeLoading, handleError, {view: target.val()});
        } else {
            Control.Ajax.del(url + 'views/' + target.val() +'/', removeLoading, handleError);
        }
    }

    function handleContributeChange(event) {
        var target = $(event.target);
        var contributeInital = $('input[name="can_contribute"]').prop('checked'),
            moderateInitial = $('input[name="can_moderate"]').prop('checked');

        if (target.attr('name') === 'can_moderate' && target.prop('checked')) {
            moderateInitial = !moderateInitial;
            $('input[name="can_contribute"]').prop('checked', true);
        }
        else if (target.attr('name') === 'can_contribute' && !target.prop('checked')) {
            contributeInital = !contributeInital;
            $('input[name="can_moderate"]').prop('checked', false);
        }
        
        var data = {
            'can_contribute': $('input[name="can_contribute"]').prop('checked'),
            'can_moderate': $('input[name="can_moderate"]').prop('checked')
        };

        function handleContributeUpdateError(response) {
            removeLoading();
            messages.showInlineError($('#permissions .panel-heading:first-child'), 'An error occurred while updating the user group. Error text was: ' + response.responseJSON.error);
            $('input[name="can_contribute"]').prop('checked', contributeInital);
            $('input[name="can_moderate"]').prop('checked', moderateInitial);
        }

        displayLoading();
        Control.Ajax.put(url, removeLoading, handleContributeUpdateError, data);
    }

    $('input.view-permission').change(handleViewActivateChange);
    $('input.group-permission').change(handleContributeChange);
}());