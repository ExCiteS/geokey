/* ***********************************************
 * Module to add and remove values from lookup fields.
 * Needs to be instancieted using new Ui.LookupPanel()
 *
 * Used in:
 * - templates/categories/field_settings.html
 * ***********************************************/

(function (global) {
    'use strict';

    /**
     * Constructor
     * @param {String} panelId The HTML element id of the lookup panel.
     * @param {String} url     The base url for AJAX request to update the field on server side.
     */
    function LookupPanel(panelId, url) {
        this.panel = $(panelId);
        this.url = url + '/lookupvalues';
        this.lookuplist = this.panel.find('ul.list-group');
        this.formField = this.panel.find('input[name="new-value"]');
        this.addButton = this.panel.find('.panel-footer button');

        // register event handlers
        this.addButton.click(this.handleAddValue.bind(this));
        this.lookuplist.find('button.edit-lookup').click(this.toggleEditForm.bind(this));
        this.lookuplist.find('button.save-edit').click(this.handleEditValue.bind(this));
        this.lookuplist.find('button.delete-lookup').click(this.handleRemoveValue.bind(this));
        this.formField.keyup(this.handleFormType.bind(this));
        this.lookuplist.find('input[name="value"]').keyup(this.handleEditType.bind(this));
    }

    /**
     * Is called after every key stroke in input[name="new-value"]. It checks,
     * whether the ENTER key was pressed and programmatically clicks the add
     * button to save the value.
     * @param {Object} event keyup event
     */
    LookupPanel.prototype.handleFormType = function handleFormType(event) {
        if (event.keyCode === 13) {
            this.addButton.click();
        }
    };

    /**
     * Is called after every key stroke in input[name="value"], when a user
     * updates the name of an exisiting field. It checks, whether the ENTER
     * key was pressed and programmatically clicks the add button to save the
     * value.
     * @param {Object} event keyup event
     */
    LookupPanel.prototype.handleEditType = function handleEditType(event) {
        if (event.keyCode === 13) {
            $(event.target).parents('.list-group-item').find('button.save-edit').click();
        }
    };

    /**
     * Displays an status message after a lookup has been added, updated or
     * removed.
     * @param {String} msg The message to be displayed, in plain English.
     * @param {String} type Either success or danger, indicates the message type (success or error)
     * @param {String} glyphicon an icon class to prepended to the message (See: http://getbootstrap.com/components/#glyphicons)
     */
    LookupPanel.prototype.displayMessage = function displayMessage(msg, type, glyphicon) {
        var target = this.panel.find('.panel-heading');
        var html = $('<div class="panel-body message bg-' + type + ' text-' + type + '"><span class="glyphicon glyphicon-' + glyphicon + '"></span> ' + msg + '</div>');

        // remove exisiting messages
        target.siblings('.message').remove();

        // add the message
        target.after(html);

        // automatically remove the message after 5 sec
        setTimeout(function () { html.remove(); }, 5000);
    };

    /**
     * Displays a success message.
     * @param {String} msg The message to be displayed, in plain English.
     */
    LookupPanel.prototype.displaySuccess = function displaySuccess(msg) {
        this.displayMessage(msg, 'success', 'ok');
    };

    /**
     * Displays a error message.
     * @param {String} msg The message to be displayed, in plain English.
     */
    LookupPanel.prototype.displayError = function displayError(msg) {
        this.displayMessage(msg, 'danger', 'remove');
    };

    /**
     * Toggles display of update form of a lookup value.
     * @param  {Event} event Click event fired by the link
     */
    LookupPanel.prototype.toggleEditForm = function toggleEditForm(event) {
        var container = $(event.target).parents('.list-group-item');
        container.find('.value-display').toggleClass('hidden');
        container.find('.value-edit').toggleClass('hidden');

        if (container.find('.value-edit').hasClass('hidden')) {
            container.find('.cancel').off('click', toggleEditForm);
        } else {
            container.find('.cancel').click(toggleEditForm);
        }
    }

    /**
     * Handles the update of a lookup. Is called when the user clicks save next
     * to the form field.
     * @param  {Event} event Click event fired by the link
     */
    LookupPanel.prototype.handleEditValue = function handleEditValue(event) {
        var container = $(event.target).parents('.list-group-item');
        var lookupId = event.target.value;
        var value = container.find('input').val();

        /**
         * Handles succesfull update of the lookup value.
         */
        function handleEditValueSucces() {
            this.displaySuccess('The value has been updated.');
            this.toggleEditForm(event);
            container.find('span.value-label').text(value)
        }

        /**
         * Handles the response after the update of a lookup value failed.
         * @param  {Object} response JSON object of the response
         */
        function handleEditValueError(response) {
            this.displayError('An error occurred while updating the lookup value. Error text was: ' + response.responseJSON.error);
        }

        Control.Ajax.patch(this.url + '/' + lookupId, handleEditValueSucces.bind(this), handleEditValueError.bind(this), {name: value} );
    }

    /**
     * Handles the removal of a lookup value from the lookup field. Is called
     * when the user clicks on the remove link next to the value.
     * @param  {Event} event Click event fired by the link
     */
    LookupPanel.prototype.handleRemoveValue = function handleRemoveValue(event) {
        var lookupId = $(event.currentTarget).val();
        var itemToRemove = $(event.currentTarget).parents('.list-group-item');

        /**
         * Handles succesfull removal of the lookup value. Removes the item from
         * the list of lookup values.
         */
        function handleRemoveValueSucces() {
            itemToRemove.remove();
            this.displaySuccess('The value has been deleted.');
        }

        /**
         * Handles the response after the removal of a lookup value failed.
         * @param  {Object} response JSON object of the response
         */
        function handleRemoveValueError(response) {
            this.displayError('An error occurred while removing the lookup value. Error text was: ' + response.responseJSON.error);
        }

        Control.Ajax.del(this.url + '/' + lookupId, handleRemoveValueSucces.bind(this), handleRemoveValueError.bind(this), {name: this.formField.val()} );

        event.preventDefault();
    };

    /**
     * Handles the addition of a lookup value to the lookup field. Is called when
     * the user clicks the 'Add' button next the bottom text field of the panel.
     */
    LookupPanel.prototype.handleAddValue = function handleAddValue(event) {
        /**
         * Handles successful addition of the lookup values. Removes all items
         * from the list of lookup values and adds the updated list that has been
         * return with the resppnse.
         * @param  {Object} response JSON object of the response
         */
        function handleAddValueSuccess(response) {
            var lookupValues = response.lookupvalues;

            this.formField.val(null);
            this.lookuplist.empty();
            this.lookuplist.append(Templates.lookupvalues(response));

            // register event handlers
            this.lookuplist.find('button.edit-lookup').click(this.toggleEditForm.bind(this));
            this.lookuplist.find('button.save-edit').click(this.handleEditValue.bind(this));
            this.lookuplist.find('button.delete-lookup').click(this.handleRemoveValue.bind(this));
            this.lookuplist.find('input[name="value"]').keyup(this.handleEditType.bind(this));
            this.addButton.button('reset');
            this.displaySuccess('The value has been added.');
        }

        /**
         * Handles the response after the addition of a lookup value failed.
         * @param  {Object} response JSON object of the response
         */
        function handleAddValueError(response) {
            this.displayError('An error occurred while adding the lookup value. Error text was: ' + response.responseJSON.error);
        }

        this.addButton.button('loading');
        Control.Ajax.post(this.url, handleAddValueSuccess.bind(this), handleAddValueError.bind(this), {name: this.formField.val()});
        event.preventDefault();
    };

    global.LookupPanel = LookupPanel;
}(window.Ui ? window.Ui : window.Ui = {}));
