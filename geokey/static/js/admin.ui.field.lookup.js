/* ***********************************************
 * Module to add and remove values from lookup fields.
 * Needs to be instancieted using new Ui.LookupPanel()
 *
 * @author Oliver Roick (http://github.com/oliverroick)
 * @version 0.1
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

        this.addButton.click(this.handleAddValue.bind(this));
        this.lookuplist.find('li a').click(this.handleRemoveValue.bind(this));
        this.formField.keyup(this.handleFormType.bind(this));
    }

    LookupPanel.prototype.handleFormType = function handleFormType(event) {
        if (event.keyCode === 13) {
            this.addButton.click();
        }
    };

    LookupPanel.prototype.displayMessage = function displayMessage(msg, type, glyphicon) {
        var target = this.panel.find('.panel-heading');
        var html = $('<div class="panel-body message bg-' + type + ' text-' + type + '"><span class="glyphicon glyphicon-' + glyphicon + '"></span> ' + msg + '</div>');
        target.siblings('.message').remove();
        target.after(html);
        setTimeout(function () { html.remove(); }, 5000);
    };

    LookupPanel.prototype.displaySuccess = function displaySuccess(msg) {
        this.displayMessage(msg, 'success', 'ok');
    };

    LookupPanel.prototype.displayError = function displayError(msg) {
        this.displayMessage(msg, 'danger', 'remove');
    };

    /**
     * Handles the removal of a lookup value from the lookup field. Is called
     * when the user clicks on the remove link next to the user name.
     * @param  {[Event} event Click event fired by the link
     */
    LookupPanel.prototype.handleRemoveValue = function handleRemoveValue(event) {
        var lookupId = $(event.target).attr('data-lookup-id');
        var itemToRemove = $(event.target).parent('.list-group-item');

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

            this.lookuplist.find('li a').click(this.handleRemoveValue.bind(this));
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
