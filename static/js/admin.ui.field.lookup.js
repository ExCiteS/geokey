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

		this.messages = new Ui.MessageDisplay();
	}

	/**
	 * Displays the success tick in the panel heading.
	 */
	LookupPanel.prototype.displaySuccess = function displaySuccess() {
		this.messages.showInlineSuccess(this.panel.find('.panel-heading'));
	};

	/**
	 * Shows the error message in the panel heading.
	 */
	LookupPanel.prototype.displayError = function displayError(message) {
		this.messages.showInlineError(this.panel.find('.panel-heading'), message);
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
			this.displaySuccess();
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
	LookupPanel.prototype.handleAddValue = function handleAddValue() {
		/**
		 * Handles successful addition of the lookup values. Removes all items
		 * from the list of lookup values and adds the updated list that has been
		 * return with the resppnse.
		 * @param  {Object} response JSON object of the response
		 */
		function handleAddValueSuccess(response) {
			var lookupValues = response.field.lookupvalues;

			this.formField.val(null);
			this.lookuplist.empty();
			for (var i = 0, len = lookupValues.length; i < len; i++) {
				this.lookuplist.append('<li class="list-group-item">' + lookupValues[i].name + ' (<a data-lookup-id="' + lookupValues[i].id + '" class="text-danger" href="#">remove</a>)</li>');
			}
			this.lookuplist.find('li a').click(this.handleRemoveValue.bind(this));
			this.addButton.button('reset');
			this.displaySuccess();
		}

		/**
		 * Handles the response after the addition of a lookup value failed.
		 * @param  {Object} response JSON object of the response
		 */
		function handleAddValueError(response) {
			this.displayError('An error occurred while adding the lookup value. Error text was: ' + response.responseJSON.error);
		}

		this.addButton.button('loading');
		Control.Ajax.put(this.url, handleAddValueSuccess.bind(this), handleAddValueError.bind(this), {name: this.formField.val()});
	};

	global.LookupPanel = LookupPanel;
}(window.Ui ? window.Ui : window.Ui = {}));