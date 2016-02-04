/* ***********************************************
 * Updates the settings of projects, categories
 * and fields. Updates private/public and
 * active/inactive, also either locks or unlocks.
 *
 * Used in:
 * - projects/project_settings.html
 * - categories/category_settings.html
 * - categories/field_settings.html
 * ***********************************************/

$(function(global) {
    'use strict';

    // Read the globals
    var url = global.url;
    var name = global.updatename;

    if (!url && !name) {
        // Read the IDs from body's attributes
        var projectId = $('body').attr('data-project-id');
        var categoryId = $('body').attr('data-category-id');
        var fieldId = $('body').attr('data-field-id');

        // The url to send the requests to update the object
        var url = 'projects/' + projectId;

        // The key to access the result object in the response
        var resultAccessor = 'project';

        // Human readable name, to be used in message displays
        var name = 'project';

        // Settings for updating a category or a field
        if (projectId && categoryId) {
            url += '/categories/' + categoryId;
            name = 'category';
        }
        if (projectId && categoryId && fieldId) {
            url += '/fields/' + fieldId;
            name = 'field';
        }
    }

    /**
     * Updates the user interface after the response is received. Resets submit buttons in modals and hides all modals.
     * Toggles the respective panel (active or public) if the request has been successful.
     * @param {String} toToggle CSS class part to toogle the display after update
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
            } else if (result === 'private') {
                $('.public').addClass('hidden');
                $('.private').removeClass('hidden');
            }
        }

        if (toToggle == 'everyone_contributes') {
            $('input[name="everyone_contributes"][value="' + result + '"]').prop('checked', true);
        }

        if (toToggle === 'locked') {
            if (result === 'locked') {
                $('.glyphicon-lock').removeClass('hidden');
            } else if (result === 'unlocked') {
                $('.glyphicon-lock').addClass('hidden');
            }
        }
    }

    function displayMessage(elementClass, msg, type, glyphicon) {
        var target = $('.toggle-' + elementClass).first();
        var html = $('<div class="message bg-' + type + ' text-' + type + '"><span class="glyphicon glyphicon-' + glyphicon + '"></span> ' + msg + '</div>');

        target.siblings('.message').remove();
        target.before(html);
        setTimeout(function() {
            html.remove();
        }, 5000);
    }

    function displaySuccess(elementClass, msg) {
        displayMessage(elementClass, msg, 'success', 'ok');
    }

    function displayError(elementClass, msg) {
        displayMessage(elementClass, msg, 'danger', 'remove');
    }

    /**
     * Handles the respionse after the update of the item failed.
     * @param {Object} response JSON object of the response
     */
    function handleError(response) {
        updateUi();
        displayError('active', 'An error occurred while updating the ' + name + '. ' + response.responseJSON.error);
    }

    /**
     * Handles the click on the confirm button and updates the status to either `active` or `inactive`.
     * @param {Event} event The click event fired by the button
     */
    function updateActive(event) {
        /**
         * Handles the respionse after the status of the item has been updated successfully.
         * @param {Object} response JSON object of the response
         */
        function handleSuccess(response) {
            updateUi('active');
            displaySuccess('active', 'The ' + name + ' is now ' + response.status + '.');
        }

        Control.Ajax.put(url, handleSuccess, handleError, {
            'status': event.target.value
        });
    }

    /**
     * Handles the click on the confirm button and updates the status to either `private` or `public`.
     * @param {Event} event The click event fired by the button
     */
    function updatePrivate(event) {
        var isPrivate = (event.target.value === 'true');

        /**
         * Handles the respionse after the status of the item has been updated successfully.
         * @param {Object} response JSON object of the response
         */
        function handleSuccess(response) {
            var result = (response.isprivate ? 'private' : 'public');

            updateUi('private', result);
            updateUi('everyone_contributes', response.everyone_contributes);
            displaySuccess('private', 'The ' + name + ' is now ' + result + '.');
        }

        Control.Ajax.put(url, handleSuccess, handleError, {
            'isprivate': isPrivate
        });
    }

    /**
     * Handles the click on the confirm button and either locks or unlocks the instance.
     * @param {Event} event The click event fired by the button
     */
    function updateLocked(event) {
        var isLocked = (event.target.value === 'true');

        /**
         * Handles the respionse after the status of the item has been updated successfully.
         * @param {Object} response JSON object of the response
         */
        function handleSuccess(response) {
            var result = (response.islocked ? 'locked' : 'unlocked');

            updateUi('locked', result);
            displaySuccess('locked', 'The ' + name + ' is now ' + result + '.');
        }

        Control.Ajax.put(url, handleSuccess, handleError, {
            'islocked': isLocked
        });
    }

    // Register event handlers
    $('#make-active-confirm button[name="confirm"]').click(updateActive);
    $('#make-inactive-confirm button[name="confirm"]').click(updateActive);
    $('#make-public-confirm button[name="confirm"]').click(updatePrivate);
    $('#make-private-confirm button[name="confirm"]').click(updatePrivate);
    $('#lock-confirm button[name="confirm"]').click(updateLocked);
    $('#unlock-confirm button[name="confirm"]').click(updateLocked);
}(this));
