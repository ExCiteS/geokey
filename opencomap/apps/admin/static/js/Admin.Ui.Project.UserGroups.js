$(function () {
	var projectId = $('body').attr('data-project-id');
	var url = 'projects/' + projectId;
	var messages = new Ui.MessageDisplay('#users');

	var $administratorsPanel = new Ui.Usergroup('#users #administrators', projectId),
		$contributorsPanel = new Ui.Usergroup('#users #contributors', projectId),
		$everyoneCheck = $('#users #contributors input[type="checkbox"]');


	function toggleEveryoneView() {
		$('#users #contributors .user-list').toggle();
		$('#users #contributors .panel-footer').toggle();
	}

	function handleEveryoneSuccess(response) {
		messages.showSuccess('The project has been updated successfully.');
		toggleEveryoneView(response.project.everyonecontributes);
	}

	function handleEveryoneError(response) {
		messages.showError('An error occurred while updating the project. ' + response.responseJSON.error);
	}

	function handleEveryoneChange(event) {
		Control.Ajax.put(url, handleEveryoneSuccess, handleEveryoneError, {'everyonecontributes': event.target.checked});
	}
	
	if ($everyoneCheck.prop('checked')) {
		$('#users #contributors .user-list').hide();
		$('#users #contributors .panel-footer').hide();
	}
	$everyoneCheck.change(handleEveryoneChange);
});