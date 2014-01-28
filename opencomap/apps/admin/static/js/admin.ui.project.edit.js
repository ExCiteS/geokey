$(function () {
	var PROJECT_ID = $('body').attr('data-project-id');
	var AJAX_URL = 'projects/' + PROJECT_ID;

	function showMessage(type, msgText) {
		var html = $('<div class="col-md-12"><div class="alert alert-' + type + '">' + msgText + '</div></div>').hide();
		$('#general-settings').prepend(html);
		html.show('slow').delay(5000).hide('slow', function() {
			html.remove();
		});
	}

	function updateUi(toToggle) {
		$('button[name="confirm"]').button('reset');
		$('.modal').modal('hide');
		if (toToggle) {
			$('.toggle-' + toToggle).toggleClass('hide');
		}
	}

	function deleteProject() {
		function handleSuccess(response) {
			updateUi()
			$('.row').remove();
			$('hr').remove();
			$('.page-header').after('<div class="col-md-12"><div class="alert alert-success">The project has now been deleted. <a href="/admin/dashboard" class="alert-link">Return to dashboard</a>.</div></div>')
		}

		function handleError(response) {
			updateUi();
			showMessage('danger', 'An error occurred while updating the project. ' + response.responseJSON.error);
		}

		Control.Ajax.del(AJAX_URL, handleSuccess, handleError);
	}

	function updateActive(event) {
		function handleSuccess(response) {
			updateUi('active');
			showMessage('success', 'The project is now ' + (response.project.status === 0 ? 'active' : 'inactive') + '.');
		}

		function handleError(response) {
			updateUi('active');
			showMessage('danger', 'An error occurred while updating the project. ' + response.responseJSON.error);
		}
		
		Control.Ajax.put(AJAX_URL, handleSuccess, handleError, {'status': parseInt(event.target.value)});
	}

	function updatePrivate(event) {
		var isPrivate = (event.target.value === 'true');

		function handleSuccess(response) {
			updateUi('private');
			showMessage('success', 'The project is now ' + (response.project.isprivate ? 'private' : 'public') + '.');
		}

		function handleError(response) {
			updateUi('private');
			showMessage('danger', 'An error occurred while updating the project. ' + response.responseJSON.error);
		}

		Control.Ajax.put(AJAX_URL, handleSuccess, handleError, {'isprivate': isPrivate});
	}

	$('#delete-confirm button[name="confirm"]').click(deleteProject);
	$('#make-inactive-confirm button[name="confirm"]').click(updateActive);
	$('#make-active-confirm button[name="confirm"]').click(updateActive);
	$('#make-public-confirm button[name="confirm"]').click(updatePrivate);
	$('#make-private-confirm button[name="confirm"]').click(updatePrivate);
});