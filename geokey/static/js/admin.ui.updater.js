/* ***********************************************
 * Connects the user inferface for updating teh settings of a project with the AJAX backend.
 * Sends requests using admin.control.ajax and handles the responses by update the interface
 * accordingly.
 *
 * @author Oliver Roick (http://github.com/oliverroick)
 * @version 0.1
 * ***********************************************/

$(function (global) {
    'use strict';
    // Read the globals; from extensions
    var url = global.url;
    var name = global.updatename;

    if (!url && !name) {
        // Read the IDs from the body's attributes
        var projectId = $('body').attr('data-project-id');
        var categoryId = $('body').attr('data-category-id');
        var fieldId = $('body').attr('data-field-id');
        var groupingId = $('body').attr('data-grouping-id');
        var groupId = $('body').attr('data-group-id');
        var appId = $('body').attr('data-app-id');

        /*
        The url to send the requests to update the object
        */
        var url = 'projects/' + projectId;

        /*
        The key to access the result object in the response
        */
        var resultAccessor = 'project';

        /*
        Human readable name, to be used in message displays
        */
        var name = 'project';

        // Setting parameters
        if (projectId && categoryId) {
            url += '/categories/' + categoryId;
            name = 'category';
        }
        if (projectId && categoryId && fieldId) {
            url += '/fields/' + fieldId;
            name = 'field';
        }
        if (projectId && groupingId) {
            url += '/views/' + groupingId;
            name = 'map';
        }
        if (projectId && groupId) {
            url += '/usergroups/' + groupId;
            name = 'user group';
        }
        if (appId) {
            url = 'apps/' + appId;
            name = 'application';
        }
    }

    /**
     * Updates the user interface after the response is received. Resets
     * submit buttons in modals and hides all modals.
     * Toggles the respective panel (active or public) if the request has
     * been successful.
     * @param  {String} toToggle Css class part to toogle the display after update
     */
    function updateUi(toToggle, result) {
        $('button[name="confirm"]').button('reset');
        $('.modal').modal('hide');
        if (toToggle) {
            $('.toggle-' + toToggle).toggleClass('hidden');
        }

        if (toToggle === 'private') {
            if (result === 'public') {
                $('.public').removeClass('hidden');
                $('.private').addClass('hidden');
            }
            else if (result === 'private') {
                $('.public').addClass('hidden');
                $('.private').removeClass('hidden');
            }
        }
    }

    function displayMessage(elementClass, msg, type, glyphicon) {
        var target = $('.toggle-' + elementClass).first();
        var html = $('<div class="message bg-' + type + ' text-' + type + '"><span class="glyphicon glyphicon-' + glyphicon + '"></span> ' + msg + '</div>');
        target.siblings('.message').remove();
        target.before(html);
        setTimeout(function () { html.remove(); }, 5000);
    }

    function displaySuccess(elementClass, msg) {
        displayMessage(elementClass, msg, 'success', 'ok');
    }

    function displayError(elementClass, msg) {
        displayMessage(elementClass, msg, 'danger', 'remove');
    }

    /**
     * Handles the click on the confirm button and updates the status to either active or inactive.
     * @param  {Event} event The click event fired by the button.
     */
    function updateActive(event) {
        /**
         * Handles the respionse after the status of the item has been updated successfully.
         * @param  {Object} response JSON object of the response
         */
        function handleSuccess(response) {
            updateUi('active');
            displaySuccess('active', 'The ' + name + ' is now ' + response.status + '.');
        }

        /**
         * Handles the respionse after the update of the item failed.
         * @param  {Object} response JSON object of the response
         */
        function handleError(response) {
            updateUi();
            displayError('active', 'An error occurred while updating the ' + name + '. ' + response.responseJSON.error);
            // messages.showPanelError(getMessageTarget('active'), 'An error occurred while updating the ' + name + '. ' + response.responseJSON.error);
        }
        Control.Ajax.put(url, handleSuccess, handleError, {'status': event.target.value});
    }

    /**
     * Handles the click on the confirm button and updates the status to either private or public.
     * @param  {Event} event The click event fired by the button.
     */
    function updatePrivate(event) {
        var isPrivate = (event.target.value === 'true');

        /**
         * Handles the respionse after the status of the item has been updated successfully.
         * @param  {Object} response JSON object of the response
         */
        function handleSuccess(response) {
            var result = (response.isprivate ? 'private' : 'public');
            updateUi('private', result);
            displaySuccess('private', 'The ' + name + ' is now ' + result + '.');
        }

        /**
         * Handles the respionse after the update of the item failed.
         * @param  {Object} response JSON object of the response
         */
        function handleError(response) {
            updateUi();
            displayError('private', 'An error occurred while updating the ' + name + '. ' + response.responseJSON.error);
        }

        Control.Ajax.put(url, handleSuccess, handleError, {'isprivate': isPrivate});
    }

    $('#make-inactive-confirm button[name="confirm"]').click(updateActive);
    $('#make-active-confirm button[name="confirm"]').click(updateActive);
    $('#make-public-confirm button[name="confirm"]').click(updatePrivate);
    $('#make-private-confirm button[name="confirm"]').click(updatePrivate);
}(this));
