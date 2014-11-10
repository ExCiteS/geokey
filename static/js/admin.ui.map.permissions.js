(function () {
    var projectId = $('body').attr('data-project-id');
    var groupingId = $('body').attr('data-grouping-id');

    function handleViewActivateChange(event) {
        var target = $(event.currentTarget);
        var url = 'projects/' + projectId + '/usergroups/' + target.attr('name') + '/';

        function handleError(response) {
            target.toggleClass('active');
            var msg = 'An error occurred while updating data grouping permissions. Error text was: ' + response.responseJSON.error;
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

    function changePrivate(event) {
        var url = 'projects/' + projectId + '/data-groupings/' + groupingId +'/';

        function handleSuccess(response) {
            var msg = '';
            if (response.isprivate) {
                msg = 'The data grouping is now hidden from the public.';
                $('button.grant-single').removeAttr('disabled');
            } else {
                msg = 'The data grouping is now accessible to the public.';
                $('button.grant-single').attr('disabled', 'disabled');
            }

            $('#grouping-visibilty > div').toggleClass('hidden');

            var html = $('<div class="message bg-success text-success"><span class="glyphicon glyphicon-ok"></span> ' + msg + '</div>');
            $('#grouping-visibilty').prepend(html);
            setTimeout(function () { html.remove(); }, 5000);
        }

        function handleError(response){
            var msg = 'An error occurred while updating the data grouping. Error text was: ' + response.responseJSON.error;
            var html = $('<div class="message bg-danger text-danger"><span class="glyphicon glyphicon-remove"></span> ' + msg + '</div>');
            $('#grouping-visibilty').prepend(html);
            setTimeout(function () { html.remove(); }, 5000);
        }

        Control.Ajax.put(url, handleSuccess, handleError, {'isprivate': $(event.currentTarget).val()});
    }

    $('button.grant-single').click(handleViewActivateChange);
    $('button#grant-all').click(grantAll);
    $('button#revoke-all').click(revokeAll);
    $('#make-public-confirm button[name="confirm"]').click(changePrivate);
    $('#make-private-confirm button[name="confirm"]').click(changePrivate);
}());
