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
	var messages = new Ui.MessageDisplay('.page-header');

	// Reads the relevant DOM elements
	var descriptionText = $('div.page-header p.lead'),
		descriptionForm = $('#description-form'),
		descriptionFormField = $('#description-form #description'),
		descriptionFormCancel = $('#description-form button[type="button"]'),
		submitbtn = $('form#description-form button[type="submit"]');

	// Reads the IDs from the body's attributes
	var projectId = $('body').attr('data-project-id'),
		featuretypeId = $('body').attr('data-featuretype-id'),
		fieldId = $('body').attr('data-field-id'),
		viewId = $('body').attr('data-view-id'),
		groupId = $('body').attr('data-group-id');

	// sets the request URL according to the IDs read above
	var url = 'projects/' + projectId;
	if (projectId && viewId) { url += '/views/' + viewId; }
	if (projectId && viewId && groupId) { url += '/usergroups/' + groupId; }
	if (projectId && featuretypeId) { url += '/featuretypes/' + featuretypeId; }
	if (projectId && featuretypeId && fieldId) { url += '/fields/' + fieldId; }


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
		// Sets the id to access the response according to the IDs read avobe
		var resultAccessor = 'project';
		if (featuretypeId) { resultAccessor = 'featuretype'; }
		if (fieldId) { resultAccessor = 'field'; }
		if (viewId) { resultAccessor = 'view'; }
		if (groupId) { resultAccessor = 'usergroup'; }

		descriptionFormField.val(response[resultAccessor].description);
		descriptionText.children('#descriptionText').text(response[resultAccessor].description);

		toggle();
		submitbtn.button('reset');
		descriptionFormField.removeClass('loading');
	}

	/**
	 * Handles the response after the update of the description failed
	 * @param  {Object} response JSON object of the response
	 */
	function handleRequestError(response) {
		submitbtn.button('reset');
		messages.showError('An error occurred while updating the description. Error text was: ' + response.responseJSON.error, true);
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