/* ***********************************************
 * Module to edit the description of an object in the top of pages.
 * Is automatically loaded when included in a page.
 *
 * @author Oliver Roick (http://github.com/oliverroick)
 * @version 0.1
 * ***********************************************/

$(function() {
	'use strict';
	// Initializes the message display
	var messages = new Ui.MessageDisplay();

	// Reads the relevant DOM elements
	var descriptionText = $('div.page-header p.lead'),
		descriptionForm = $('#description-form'),
		descriptionFormField = $('#description-form #description'),
		descriptionFormCancel = $('#description-form button[type="button"]'),
		submitbtn = $('form#description-form button[type="submit"]');

	// Reads the IDs from the body's attributes
	var projectId = $('body').attr('data-project-id'),
		observationtypeId = $('body').attr('data-observationtype-id'),
		fieldId = $('body').attr('data-field-id'),
		viewId = $('body').attr('data-view-id'),
		groupId = $('body').attr('data-group-id');

	// sets the request URL according to the IDs read above
	var url = 'projects/' + projectId;
	if (projectId && viewId) { url += '/views/' + viewId; }
	if (projectId && viewId && groupId) { url += '/usergroups/' + groupId; }
	if (projectId && observationtypeId) { url += '/observationtypes/' + observationtypeId; }
	if (projectId && observationtypeId && fieldId) { url += '/fields/' + fieldId; }

	/**
	 * Toggles between the display of description text and description form.
	 */
	function toggle() {
		descriptionText.toggleClass('hidden');
		descriptionForm.toggleClass('hidden');
	}

	/**
	 * Handles the response after a successful update of the description and updates the interfaces
	 * @param  {Object} response JSON object of the response
	 */
	function handleRequestSucess(response) {
		descriptionFormField.val(response.description);
		descriptionText.children('#descriptionText').text(response.description);

		toggle();
		submitbtn.button('reset');
		descriptionFormField.removeClass('loading');
		messages.showInlineSuccess(descriptionText.children('#descriptionText'));
	}

	/**
	 * Handles the response after the update of the description failed
	 * @param  {Object} response JSON object of the response
	 */
	function handleRequestError(response) {
		submitbtn.button('reset');
		messages.showInlineError(descriptionForm, 'An error occurred while updating the description. Error text was: ' + response.responseJSON.error);
		descriptionFormField.removeClass('loading');
	}

	/**
	 * Sends the update request after the submission button has been clicked
	 * @param  {Event} event The click event on the body
	 */
	function handleDescriptionSubmit(event) {
		submitbtn.button('loading');
		descriptionFormField.addClass('loading');
		Control.Ajax.put(url, handleRequestSucess, handleRequestError, {'description': descriptionFormField.val()});

		event.preventDefault();
	}

	$('button#edit').click(toggle);
	descriptionFormCancel.click(toggle);
	descriptionForm.submit(handleDescriptionSubmit);
});