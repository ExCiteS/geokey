/* ***********************************************
 * Mangages project administrator and contributor groups.
 * Members are managed using admin.ui.usergroup.js
 *
 * @author Oliver Roick (http://github.com/oliverroick)
 * @version 0.1
 * ***********************************************/

$(function () {
	'use strict';

	var projectId = $('body').attr('data-project-id');
	var url = 'projects/' + projectId;
	var messages = new Ui.MessageDisplay('#users');

	var administratorsPanel = new Ui.Usergroup('#users #administrators', projectId),
		contributorsPanel = new Ui.Usergroup('#users #contributors', projectId),
		everyoneCheck = $('#users #contributors input[type="checkbox"]');

	/**
	 * Toggles the display of the contributors user group member list, when the user clicks the 
	 * 'everyone can contribute' checkbox.
	 */
	function toggleEveryoneView() {
		$('#users #contributors .user-list').toggle();
		$('#users #contributors .panel-footer').toggle();
	}

	/**
	 * Handles the reponse after a successful update.
	 * @param  {Object} response JSON object of the response
	 */
	function handleEveryoneSuccess(response) {
		messages.showSuccess('The project has been updated successfully.');
		toggleEveryoneView(response.project.everyonecontributes);
	}

	/**
	 * Handles the reponse after the update failed.
	 * @param  {Object} response JSON object of the response
	 */
	function handleEveryoneError(response) {
		// TODO: Reset checkbox after the update failes.
		messages.showError('An error occurred while updating the project. ' + response.responseJSON.error);
	}

	/**
	 * Handles the change of the 'everyone can contribute' checkbox.
	 * @param  {Event} event The change event of the checkbox.
	 */
	function handleEveryoneChange(event) {
		Control.Ajax.put(url, handleEveryoneSuccess, handleEveryoneError, {'everyonecontributes': event.target.checked});
	}
	
	if (everyoneCheck.prop('checked')) {
		$('#users #contributors .user-list').hide();
		$('#users #contributors .panel-footer').hide();
	}
	everyoneCheck.change(handleEveryoneChange);
});