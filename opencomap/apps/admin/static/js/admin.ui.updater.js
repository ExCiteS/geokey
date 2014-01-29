/* ***********************************************
 * Connects the user inferface for updating teh settings of a project with the AJAX backend. 
 * Sends requests using admin.control.ajax and handles the responses by update the interface
 * accordingly.
 *
 * @author Oliver Roick
 * @version 0.1
 * ***********************************************/
 
$(function () {
	var messages = new Ui.MessageDisplay('#general-settings');

	var projectId = $('body').attr('data-project-id');
	var featuretypeId = $('body').attr('data-featuretype-id');

	var url = 'projects/' + projectId;
	var resultAccessor = 'project';
	var name = 'project';
	
	if (featuretypeId) { 
		url += '/featuretypes/' + featuretypeId; 
		resultAccessor = 'featuretype';
		name = 'feature type';
	}

	/**
	 * Updates the user interface after the response is received. Resets submit buttons in modals and hides all modals. 
	 * Toggles the respective panel (active or public) if the request has been successful.
	 */
	function updateUi(toToggle) {
		$('button[name="confirm"]').button('reset');
		$('.modal').modal('hide');
		if (toToggle) {
			$('.toggle-' + toToggle).toggleClass('hidden');
		}
	}

	/**
	 * Deletes the project.
	 */
	function del() {
		function handleSuccess(response) {
			updateUi()
			$('.row').remove();
			$('hr').remove();
			$('.page-header').after('<div class="col-md-12"><div class="alert alert-success">The project has now been deleted. <a href="/admin/dashboard" class="alert-link">Return to dashboard</a>.</div></div>')
		}

		function handleError(response) {
			updateUi();
			messages.showError('An error occurred while updating the ' + name + '. ' + response.responseJSON.error);
		}

		Control.Ajax.del(url, handleSuccess, handleError);
	}

	/**
	 * Updates the active status of the project.
	 */
	function updateActive(event) {
		function handleSuccess(response) {
			updateUi('active');
			messages.showSuccess('The ' + name + ' is now ' + (response[resultAccessor].status === 0 ? 'active' : 'inactive') + '.');
		}

		function handleError(response) {
			updateUi();
			messages.showError('An error occurred while updating the ' + name + '. ' + response.responseJSON.error);
		}
		Control.Ajax.put(url, handleSuccess, handleError, {'status': parseInt(event.target.value)});
	}

	/**
	 * Updates the private status of the project.
	 */
	function updatePrivate(event) {
		var isPrivate = (event.target.value === 'true');

		function handleSuccess(response) {
			updateUi('private');
			messages.showSuccess('The ' + name + ' is now ' + (response[resultAccessor].isprivate ? 'private' : 'public') + '.');
		}

		function handleError(response) {
			updateUi();
			messages.showError('An error occurred while updating the ' + name + '. ' + response.responseJSON.error);
		}

		Control.Ajax.put(url, handleSuccess, handleError, {'isprivate': isPrivate});
	}

	$('#delete-confirm button[name="confirm"]').click(del);
	$('#make-inactive-confirm button[name="confirm"]').click(updateActive);
	$('#make-active-confirm button[name="confirm"]').click(updateActive);
	$('#make-public-confirm button[name="confirm"]').click(updatePrivate);
	$('#make-private-confirm button[name="confirm"]').click(updatePrivate);
});