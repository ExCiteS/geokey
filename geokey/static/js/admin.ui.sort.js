$(function () {
    var projectId = $('body').attr('data-project-id'),
        categoryId = $('body').attr('data-category-id'),
        url = 'projects/' + projectId + '/categories/',
        name = 'category';

        if (categoryId) {
            url += categoryId + '/fields/';
            name = 'field';
        }

        url += 're-order/';

    var list = $( "#sortable" );

    function handleSuccess() {
        $('.message').remove();
        var msg = 'The ' + name + ' order has been saved successfully.';
        var html = $('<div class="bg-success text-success message"><span class="glyphicon glyphicon-ok"></span> ' + msg + '</div>');
            $('#sortable').before(html);
            setTimeout(function () { html.remove(); }, 5000);
    }

    function handleError(response) {
        $('.message').remove();
        var msg = 'An error occurred while updating the ' + name + ' order. Error text was: ' + response.responseJSON.error;
        var html = $('<div class="bg-danger text-danger message"><span class="glyphicon glyphicon-remove"></span>' + msg + '</div>');
            $('#sortable').before(html);
            setTimeout(function () { html.remove(); }, 5000);
        list.sortable( "cancel" );
    }

    function getSorting() {
        var sort = [];
        var fields = list.children();

        for (var i = 0, len = fields.length; i < len; i++) {
            sort.push($(fields[i]).attr('data-item-id'));
        }

        Control.Ajax.post(url, handleSuccess, handleError, {'order': sort});
    }

    list.sortable({
        placeholder: 'ui-state-highlight',
        stop: getSorting,
        revert: true
    });
    $( "#sortable" ).disableSelection();
}());
