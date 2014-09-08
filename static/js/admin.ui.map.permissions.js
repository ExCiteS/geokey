(function () {
    var projectId = $('body').attr('data-project-id');
    var viewId = $('body').attr('data-view-id');

    function handleViewActivateChange(event) {
        var target = $(event.currentTarget);
        var url = 'projects/' + projectId + '/usergroups/' + target.attr('name') + '/';

        function handleError(response) {
            target.toggleClass('active');
            var msg = 'An error occurred while updating map permissions. Error text was: ' + response.responseJSON.error;
            var html = $('<div class="bg-danger text-danger message"><span class="glyphicon glyphicon-remove"></span> ' + msg + '</div>');
            target.before(html);
            setTimeout(function () { html.remove(); }, 5000);
        }

        function handleSuccess(response) {
            var btnText = $('<span class="text-success">Grant access</span>');
            var msg = 'Access revoked.'
            if (target.hasClass('active')) {
                btnText = $('<span class="text-danger">Revoke access</span>');
                msg = 'Access granted.'
            }
            target.children().remove();
            target.append(btnText);
            
            var html = $('<div class="bg-success text-success message"><span class="glyphicon glyphicon-ok"></span> ' + msg + '</div>');
            target.before(html);
            setTimeout(function () { html.remove(); }, 5000);
        }
        
        if (target.hasClass('active')) {
            Control.Ajax.del(url + 'views/' + viewId +'/', handleSuccess, handleError);
        } else {
            Control.Ajax.post(url + 'views/', handleSuccess, handleError, {view: viewId});
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
}());