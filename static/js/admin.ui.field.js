/* ***********************************************
 * Module to edit field properties. Is currently only responsible
 * for setting minimim and maximum values of numeric fields.
 * Is automatically loaded when included in a page.
 *
 * @author Oliver Roick (http://github.com/oliverroick)
 * @version 0.1
 * ***********************************************/

$(function() {
	'use strict';

	// Reads the IDs from the body's attributes
	var projectId = $('body').attr('data-project-id'),
		observationtypeId = $('body').attr('data-observationtype-id'),
		fieldId = $('body').attr('data-field-id'),
		url = 'projects/' + projectId + '/observationtypes/' + observationtypeId + '/fields/' + fieldId;

	// Initialize the lookup panel functionality if the field is a lookup
	var lookupPanel = ($('#lookupValuesPanel').length !== 0 ? new Ui.LookupPanel('#lookupValuesPanel', url) : undefined);

	// Reads the relevant DOM elements
	var valuesSubmitBtn = $('form#valuesForm button[type="submit"]');
	var messages = new Ui.MessageDisplay('#constraints');

	/**
	 * Handles the response if the update of the numeric fields failed. Displays
	 * an error message.
	 * @param  {Object} response JSON object of the response
	 */
	function handleNumericUpdateError(response) {
		valuesSubmitBtn.button('reset');
		messages.showError('An error occured while updating the field. Error text was: ' + response.responseJSON.error + '.');
	}

	/**
	 * Handles the response if the update of the numeric fields has been
	 * successful.
	 * @param  {Object} response JSON object of the response
	 */
	function handleNumericUpdateSuccess(response) {
		$('form#valuesForm input[name="minval"]').attr('value', response.minval);
		$('form#valuesForm input[name="maxval"]').attr('value', response.maxval);
		valuesSubmitBtn.button('reset');
	}

	/**
	 * Event handler for form submission. Reads the values from the from and
	 * sends the Ajax request.
	 * @param  {Event} event The event the fires the event handler.
	 */
	function submitForm(event) {
		if (event.target.checkValidity()) {
			valuesSubmitBtn.button('loading');
			var form = $(event.target).serializeArray();
			var values = {};
			for (var i = 0, len = form.length; i < len; i++) {
				values[form[i].name] = (parseFloat(form[i].value));
			}
			Control.Ajax.put(url, handleNumericUpdateSuccess, handleNumericUpdateError, values);
		}
		event.preventDefault();
	}

	function handleNumericFieldEdit(event) {
		var target = $(event.target);

		if (target.attr('id') === 'minval') {
			$('form#valuesForm input#maxval').attr('min', target.val());
		} else if (target.attr('id') === 'maxval') {
			$('form#valuesForm input#minval').attr('max', target.val());
		}
	}

	$('form#valuesForm input[type="number"]').change(handleNumericFieldEdit);
	$('form#valuesForm').submit(submitForm);
});