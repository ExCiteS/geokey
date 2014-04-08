/* ***********************************************
 * Mangages view groups. Used to update the permissions.
 * Members are managed using admin.ui.usergroup.js
 *
 * @author Oliver Roick (http://github.com/oliverroick)
 * @version 0.1
 * ***********************************************/

$(function() {
	'use strict';
	var projectId = $('body').attr('data-project-id'),
		viewId = $('body').attr('data-view-id'),
		groupId = $('body').attr('data-group-id');

	var url = 'projects/' + projectId + '/views/' + viewId + '/usergroups/' + groupId;

	var usergroupPanel =  new Ui.Usergroup('#users #members', projectId, viewId),
		messages = new Ui.MessageDisplay();

	/**
	 * Handles the change of the checkbox status in the permission panel of the user group.
	 * @param  {Event} event The change event that has been fired by the checkbox.
	 */
	function handlePermissionChange(event) {
		var data = {};
		var target = $(event.target).parents('.checkbox');
		var state = $(event.target).prop('checked');

		/**
		 * Handles the response after the update of the permissions failed.
		 * @param  {Object} response JSON object of the response
		 */
		function handleGroupUpdateError(response) {
			$(event.target).prop('checked', !state); // reset the status of the checkbox
			messages.showInlineError(target, 'An error occurred while updating permissions of this user group. Error text was: ' + response.responseJSON.error);
		}

		/**
		 * Handles the response after a successful update of the permissions.
		 */
		function handleGroupUpdateSuccess() {
			messages.showInlineSuccess(target);
		}

		data[event.target.name] = state;
		Control.Ajax.put(url, handleGroupUpdateSuccess, handleGroupUpdateError, data);
	}

	$('#permissions input[type="checkbox"]').change(handlePermissionChange);
});