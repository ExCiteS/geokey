/* ***********************************************
 * Handles sorting of categories or fields.
 * Based in jQueryUI sortable: https://jqueryui.com/sortable/
 *
 * Used in:
 * - templates/categories/category_list.html
 * - templates/categories/category_overview.html
 * ***********************************************/

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

    /**
     * Handle successful update via the Ajax API. Displays a success message.
     */
    function handleSuccess() {
        $('.message').remove();
        var msg = 'The ' + name + ' order has been saved successfully.';
        var html = $('<div class="bg-success text-success message"><span class="glyphicon glyphicon-ok"></span> ' + msg + '</div>');
            $('#sortable').before(html);
            setTimeout(function () { html.remove(); }, 5000);
    }

    /**
     * Handle errors while updating via the Ajax API. Displays an error message
     * and reverts the order.
     */
    function handleError(response) {
        $('.message').remove();
        var msg = 'An error occurred while updating the ' + name + ' order. Error text was: ' + response.responseJSON.error;
        var html = $('<div class="bg-danger text-danger message"><span class="glyphicon glyphicon-remove"></span>' + msg + '</div>');
            $('#sortable').before(html);
            setTimeout(function () { html.remove(); }, 5000);
        list.sortable( "cancel" );
    }

    /**
     * Returns an array of ids, ordered according to the new order and sends a
     * request to update the order to the API.
     */
    function getSorting() {
        var sort = [];
        var fields = list.children();

        for (var i = 0, len = fields.length; i < len; i++) {
            sort.push($(fields[i]).attr('data-item-id'));
        }

        Control.Ajax.post(url, handleSuccess, handleError, {'order': sort});
    }

    // initialise drag and drop ordering
    list.sortable({
        placeholder: 'ui-state-highlight',
        stop: getSorting,
        revert: true
    });
    $( "#sortable" ).disableSelection();
}());
